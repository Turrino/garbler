from Utils import Utils
import random

class Event:
    def __init__(self, crumbs, garbler, chosinator):
        self.crumbs = crumbs
        self.current_block = None
        self.entry_point_type = self.crumbs.entry_point_type
        self.chosinator = chosinator
        self.garbler = garbler
        self.tracker = []
        self.story_cache = {}
        self.text = ""

    def set_text(self):
        self.text = ""
        for node in self.tracker:
            for item in node["text"]:
                self.text += " "+item

    def run_to_end(self):
        go_to_block = self.entry_point_type

        while go_to_block is not None:
            self.current_block = Utils.any_of_many(self.crumbs.blocks[go_to_block])
            go_to_block = self.advance_nodes()

        self.set_text()

    def advance_nodes(self):
        branches = self.current_block["branches"]
        current_node = {}
        go_to = 1
        node_tracker = {"type": self.current_block["type"], "text": [],
                        "canvas": self.current_block["canvas_id"], "meta" : [],
                        "node_ids": []}

        while go_to is not None:
            current_node = branches[go_to]
            node_tracker["node_ids"].append(go_to)

            parsed_text = Utils.stuff_the_blanks(current_node["situation"],
                                                 self.story_cache, self.garbler.get_element)
            node_tracker["text"].append(parsed_text[0])
            meta = parsed_text[1]
            node_tracker["meta"].append(meta)
            if "drops" in current_node.keys():
                self.process_drops(current_node["drops"])
            go_to = self.calculate_fork(current_node)

        self.tracker.append(node_tracker)

        if "terminal" in current_node.keys():
            return current_node["terminal"]
        elif "out" in self.current_block:
            return self.current_block["out"]
        else:  # No "out" means stop looking for more blocks
            return None

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
            return self.chosinator.choose(node["choice"])
        return None

    def process_drops(self, drops):
        if type(drops) is str:
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
                    self.crumbs.main_char["items"].append(self.garbler.create_item(item_drop))