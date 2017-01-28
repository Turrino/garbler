from Utils import Utils


class Event:
    def __init__(self, crumbs, entry_point_type, garbler):
        self.crumbs = crumbs
        self.current_block = None
        self.fundamentals = {}
        self.entry_point_type = entry_point_type
        self.garbler = garbler
        self.tracker = []
        self.story_cache = {}

    def run_to_end(self):
        go_to_block = self.entry_point_type

        while go_to_block is not None:
            self.current_block = Utils.any_of_many(self.crumbs.blocks[go_to_block])
            go_to_block = self.advance_nodes()

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
            # todo process drops here, add to tracker
            go_to = self.calculate_fork(current_node)

        self.tracker.append(node_tracker)

        if "terminal" in current_node.keys():
            return current_node["terminal"]
        elif "out" in self.current_block:
            return self.current_block["out"]
        else:  # No "out" means stop looking for more blocks
            return None

    def calculate_fork(self, node):
        if "fork" not in node.keys():
            return None
        for option in node["fork"]:
            if option["if"] is None:
                return option["to"]
            else:
                ands = [condition.apply(self.fundamentals) for condition in option["if"]["and"]]
                ors = [condition.apply(self.fundamentals) for condition in option["if"]["or"]]
                if ands.count(True) == len(ands) or True in ors:
                    return option["to"]
        raise ValueError('descriptive error here')