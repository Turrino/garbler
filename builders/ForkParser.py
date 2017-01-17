from builders.ModParser import ModParser

class ForkParser:
    @staticmethod
    def parse(block, mods):
        branch_ids = []
        for item in block["branches"]:
            branch_ids.append(item["id"])
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
                            if conditions[0] not in ['and', 'or']:
                                if conditions[0] == 'if':
                                    conditions[0] = 'and'
                                else:
                                    raise ValueError('descriptive error here')

                            condition = mods[conditions[1]] if conditions[1] in mods.keys()\
                                else ModParser.parse(conditions[1])
                            parsed_cond[conditions[0]].append(condition)
                            conditions = conditions[2:]

                        fork_entry["if"] = parsed_cond

                    # End of individual instruction
                    fork_entry.pop("instructions")

                    fork.append(fork_entry)
                item["fork"] = fork

        ForkParser.check_pointers(block, branch_ids)

        return block


    @staticmethod
    def check_pointers(block, branch_ids):
        # Go over the parsed forks again, see if their pointers make sense
        for item in block["branches"]:
            if "fork" in item.keys():
                for entry in item["fork"]:
                    if entry["to"] not in branch_ids:
                        raise ValueError('descriptive error here')
        return




