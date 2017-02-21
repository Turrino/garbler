from .Utils import Utils
from models.Models import Choice
from models.Models import Option
import random

class Event:
    def __init__(self, crumbs, fetcher):
        self.crumbs = crumbs
        self.current_block = None
        self.current_node = None
        self.tracking_element = None
        self.tracker = []
        self.entry_point_type = self.crumbs.entry_point_type
        self.fetcher = fetcher
        self.story_cache = {}
        self.text = ""
        self.complete = False
        self.drawed = None

    def set_text(self):
        self.text = ""
        for node in self.tracker:
            for item in node["text"]:
                self.text += " "+item

    def step(self, resume_from=None):
        if resume_from is None:
            pointer = self.entry_point_type
            resume = False
        else:
            pointer = -1
            resume = True

        while resume or (pointer is not None and not isinstance(pointer, Choice)):
            if resume:
                resume = False
            else:
                self.current_block = Utils.any_of_many(self.crumbs.blocks[pointer])
                self.prepare_block_arguments(self.current_block)
            pointer = self.advance_nodes(resume_from)
            resume_from = None

        self.set_text()

        if isinstance(pointer, Choice):
            return pointer

        self.complete = True

    def advance_nodes(self, resume_from=None):
        if resume_from is not None:
            go_to = resume_from
        else:
            go_to = "1"
            self.tracking_element = self.prepare_block_meta()

        while go_to is not None and not isinstance(go_to, Choice):
            self.current_node = self.current_block["branches"][go_to]
            self.tracking_element["node_ids"].append(go_to)

            parsed_text = Utils.stuff_the_blanks(self.current_node["situation"],
                                                 self.story_cache, self.fetcher.get_element)
            self.tracking_element["text"].append(parsed_text[0])
            meta = parsed_text[1]
            self.tracking_element["meta"].append(meta)
            if "drops" in self.current_node.keys():
                self.process_drops(self.current_node["drops"])
            go_to = self.calculate_fork(self.current_node)

        if isinstance(go_to, Choice):
            return go_to
        else:
            self.tracker.append(self.tracking_element)
            if "terminal" in self.current_node.keys():
                return self.current_node["terminal"]
            elif "out" in self.current_block:
                return self.current_block["out"]
            else:  # No "out" means stop looking for more blocks
                return None

    def prepare_block_arguments(self, block):
        if "out_args" in block.keys():
            for out_arg in block["out_args"]:
                if out_arg not in self.story_cache.keys():
                    if "primers" in block.keys() and out_arg in block["primers"].keys():
                        primer_reference = block["primers"][out_arg]
                    else:
                        # use the default primer if there isn't one specified
                        # default primers have the same name as the argument they represent
                        primer_reference = out_arg

                    primer = self.crumbs.primers[out_arg][primer_reference]
                    cache_id = out_arg

                    def cache_element(primer_instructions, qualified_name):
                        #todo allow lists in here? maybe
                        element = self.fetcher.get_element(primer_instructions)
                        self.story_cache[qualified_name] = element

                    def unpack_instructions(primer_dict, base_name):
                        for k, v in primer_dict.items():
                            if isinstance(v, str):
                                cache_element(v, base_name + "." + k)
                            else:
                                unpack_instructions(v, base_name + "." + k)

                    #check if it is a complex (dict) primer, in which case it's multiple instructions
                    if isinstance(primer, dict):
                        # todo: this is to make sure we don't unpack them multiple times; find a better way so that we don't have useless stuff in the dictionary
                        self.story_cache[primer_reference] = None
                        unpack_instructions(primer, cache_id)
                    else:
                        cache_element(primer, cache_id)

    def prepare_block_meta(self):
        if "location_types" in self.current_block.keys():
            loc_type = Utils.any_of_many(self.current_block["location_types"], False)
        else:
            loc_type = "location"
        location = self.fetcher.get_element(loc_type)
        #todo change this and similar DTOs into named tuples
        node_tracker = {"type": self.current_block["type"], "text": [],
                        "location": location, "meta" : [],
                        "node_ids": []}

        return node_tracker

    def calculate_fork(self, node):
        keys = node.keys()
        if "fork" in keys:
            for option in node["fork"]:
                if option["if"] is None:
                    return option["to"]
                else:
                    ands = [condition.apply(self.crumbs.fundamentals) for condition in option["if"]["and"]]
                    ors = [condition.apply(self.crumbs.fundamentals) for condition in option["if"]["or"]]
                    if ands.count(True) == len(ands) or True in ors:
                        return option["to"]
            raise ValueError('descriptive error here')
        elif "choice" in keys:
            return Choice(node["situation"], [Option(o["to"], o["level"], o["text"]) for o in node["choice"]])
        return None

    def process_drops(self, drops):
        if isinstance(drops, str):
            drops = self.crumbs.drops[drops]

        if "ld" in drops and drops["ld"] != 0:
            if (drops["ld"] < 0):
                self.crumbs.main_char["ld"] -= random.randrange(0, -drops["ld"])
            else:
                self.crumbs.main_char["ld"] = random.randrange(0, drops["ld"])
        if "items" in drops and drops["items"] != 0:
            # each element contains: 0 = item type, 1 = tier upper limit, 2 = drop chance %
            for item_drop in drops["items"]:
                if random.randrange(0, 100) < item_drop[2]:
                    self.crumbs.main_char["items"].append(self.fetcher.create_item(item_drop))