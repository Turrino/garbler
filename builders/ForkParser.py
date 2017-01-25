from builders.ModParser import ModParser

class ForkParser:
    @staticmethod
    def parse(block, mods, attributes):
        for key, item in block["branches"].items():
            if "fork" in item.keys():
                fork = []
                split = item["fork"].split(";")
                for entry in split:
                    # split may leave empty strings at the end or beginning - filter those out
                    fork_entry = {"instructions": list(filter(lambda x: x != '', entry.split(" ")))}

                    # Entry section
                    level = 0
                    if fork_entry["instructions"][0] != 'to':
                        outcome_symbols = ['+', '-']

                        connotation = fork_entry["instructions"][0]
                        count = len(connotation)
                        consistent = connotation.count(connotation[0]) == count

                        if fork_entry["instructions"][0][0] not in outcome_symbols or not consistent:
                            raise ValueError('descriptive error here')

                        level = count if connotation[0] == '+' else count * -1

                        fork_entry["instructions"] = fork_entry["instructions"][1:]

                    fork_entry["level"] = level

                    # Pointer section
                    if fork_entry["instructions"][0] != 'to':
                        raise ValueError('descriptive error here')

                    fork_entry["to"] = int(fork_entry["instructions"][1])
                    fork_entry["instructions"] = fork_entry["instructions"][2:]

                    # If section
                    fork_entry["if"] = None

                    if len(fork_entry["instructions"]) != 0:
                        if fork_entry["instructions"][0] != 'if':
                            raise ValueError('descriptive error here')

                        conditions = fork_entry["instructions"]

                        parsed_cond = {"and": [], "or": []}

                        while len(conditions) > 0:
                            append_to = conditions[0]
                            if append_to not in ['and', 'or']:
                                if append_to == 'if':
                                    append_to = 'and'
                                else:
                                    raise ValueError('descriptive error here')

                            if conditions[1] in mods.keys():
                                condition = mods[conditions[1]]
                                conditions = conditions[2:]
                            else:
                                to_parse = conditions[1:]
                                # check if there are multiple conditions, and split them
                                for i in range(0, len(to_parse)):
                                    if to_parse[i] in ['and', 'or']:
                                        to_parse = to_parse[:i]
                                        break

                                condition = ModParser.parse(to_parse, attributes)
                                conditions = conditions[len(to_parse)+1:]

                            parsed_cond[append_to].append(condition)


                        fork_entry["if"] = parsed_cond

                    # End of individual instruction
                    fork_entry.pop("instructions")

                    fork.append(fork_entry)
                item["fork"] = fork

        ForkParser.check_pointers(block)

        return block

    @staticmethod
    def check_pointers(block):
        # Go over the parsed forks again, see if their pointers make sense
        for key, item in block["branches"].items():
            if "fork" in item.keys():
                for entry in item["fork"]:
                    if entry["to"] not in block["branches"].keys():
                        raise ValueError('descriptive error here')
        return




