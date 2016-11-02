from collections import Counter
import random
import math
import re
from Manifest import *


class Garbler:
    def __init__(self, parsed_crumbs, peep, config):
        self.crumbs = parsed_crumbs
        self.peep = peep
        self.config = config
        self.ld_spend = config.ld_spend
        self.ld_activation = config.starting_ld*config.ld_activator
        peep.desc = self.writerer(self.crumbs['characters'], peep.gender)
        self.random_mod = config.random_mod
        # how many event-level patterns can we choose from
        self.event_pattern_range = len(self.crumbs['event_patterns'])


    def any_of_many(self, crumblist, discard_item=True):
        randomness = random.randrange(0, len(crumblist))
        item = crumblist[randomness]
        if discard_item:
            crumblist.remove(item)
        return item


    def stuff_the_blanks(self, parameters_text):
        displayables = []

        #test, remove
        #parameters_text = 'bla @items#3,1@ and @items#4@ and blah and this one @creatures@ blah'

        positions = [pos for pos, char in enumerate(parameters_text) if char == '@']
        if len(positions) % 2 != 0:
            raise ValueError("tags (@) are not even in text: {0}".format(parameters_text))

        subs = []
        overlay_metadata = []
        for i in range(0, len(positions), 2):
            #create a list of (replacement type, [repl startpos, repl endpos])
            subs.append((parameters_text[positions[i]:positions[i+1]+1], [positions[i], positions[i+1]+1]))
        for sub in subs:
            replacement = sub[0]
            display_data = replacement.find('#')
            if display_data: #trim+save the overlay data and leave the clean replacement
                splat = replacement.split('#')
                overlay_pos = (splat[1][:-1]).split(',') if replacement.find(',') else splat[1][:-1]
                overlay_metadata.append((splat[0][1:], overlay_pos)) #to do: fill metadata with more information than just the replacement type/channel
                replacement = splat[0][1:]
            #TO DO: fix this so it doesn't crash. + add the option to save metadata to pass down to other outcomes.
            parameters_text = parameters_text[:sub[1][0]] + self.get_element(replacement) + parameters_text[sub[1][1]:]

        return parameters_text


    def writerer(self, crumbset, subset=None):
        fetch_crumb = self.any_of_many

        # We use this only if a subset parameter (mood, gender...) is passed in, in order to access the sub-features
        # Then check if the selected element is a list - some elements are universal and do not have a subset
        def fetch_subset(words):
            pick = self.any_of_many(words)
            return pick[subset] if type(pick) is list else pick

        if subset is not None:
            fetch_crumb = fetch_subset

        wroted = ""

        for wordlist in crumbset:
            wroted = "{0} {1}".format(wroted, fetch_crumb(wordlist))

        return wroted[1:]


    def get_peep(self, name, attrib, gender=None):
        if gender is None:
            gender = random.randrange(0, 2)

        peep = Peep(name, attrib, gender)
        peep.desc = self.writerer(self.crumbs['characters'], gender)
        return peep


    def get_place(self, gender=None):
        return Place(self.writerer(self.crumbs['locations']))


    def get_element(self, category):
        return self.writerer(self.crumbs[category], -1)


    def create_item(self, item_drop):
        name = self.writerer(self.crumbs["items"][item_drop[0]])
        tier = random.randrange(1, item_drop[1]+1)

        points = tier*2
        minimum_allocation = math.floor(points/10) if points/10>1 else 1
        durability = random.randrange(minimum_allocation, points-minimum_allocation+1)
        modpoints = points - durability
        # pick modifiers that are consistent with that item type; make a copy of the list so that we're not removing things permanently
        attributes_list = list(self.crumbs["item_attributes_matrix"][item_drop[0]])
        chosen_attributes = []

        while modpoints > 0:
            if modpoints == 1:
                chosen_attributes.append(Attribute(self.any_of_many(attributes_list), 1.1))
                modpoints -= 1
            else:
                if (len(attributes_list) > 1):
                    allocation = math.floor(modpoints/2)
                else:
                    allocation = modpoints

                modpoints -= allocation
                #50% chance, half the points go into one mod, 50% chance they go into two mods
                multiple_allocation = random.randrange(0,2)
                if multiple_allocation and len(attributes_list) > 2:
                    chosen_attributes.append(Attribute(self.any_of_many(attributes_list), 1+allocation/20))
                    chosen_attributes.append(Attribute(self.any_of_many(attributes_list), 1+allocation/20))
                else:
                    chosen_attributes.append(Attribute(self.any_of_many(attributes_list), 1 + allocation/10))

        return Item(item_drop[0], chosen_attributes, durability, name)


    def process_drops(self, drops):
        if "ld" in drops and drops["ld"] != 0:
            if (drops["ld"] < 0):
                self.peep.ld -= random.randrange(0, -drops["ld"])
            else:
                self.peep.ld += random.randrange(0, drops["ld"])
        if "items" in drops and drops["items"] != 0:
            # each element contains: 0 = item type, 1 = tier upper limit, 2 = drop chance %
            for item_drop in drops["items"]:
                if random.randrange(0, 100) < item_drop[2]:
                    self.peep.items.append(self.create_item(item_drop))

    def outcome_calculator(self, segment, ld_active):
        # 1 is the basic value for an outcome to happen
        # the higher, the more likely it will be picked
        # can go below 1 but not below 0
        outcome_tally = [1] * len(segment.outcomes)

        for mod in segment.filtr.char_mod:
            if mod.id in self.peep.attributes:
                # each multiplier is a list of two integers, the first represents the outcome we want to affect
                # and the second is the actual likelyhood multiplier value (which can be more or less than 1)
                for multiplier in mod.multipliers:
                    outcome_tally[multiplier[0] - 1] *= multiplier[1]

        top_tally = max(outcome_tally)

        random_modifier = top_tally * self.random_mod
        outcome_tally = list(map(lambda o: (o - (random.randrange(0, int(random_modifier * 100))) / 100), outcome_tally))
        top_tally = max(outcome_tally)

        selected_outcome = [i for i, j in enumerate(outcome_tally) if j == top_tally]

        index = 0

        if len(selected_outcome) != 1:
            index = random.randrange(0, len(selected_outcome))

        finalised = segment.outcomes[int(selected_outcome[index])]

        if finalised.connotation in ['l', 'n'] and ld_active and self.try_with_some_lucky_dust():
            print("sparkly sparkle")
            for otc in segment.outcomes:
                if otc.connotation == 'w':
                    otc.ld_sparkle = True
                    finalised = otc
                    break

        if len(finalised.drops) > 0:
            self.process_drops(finalised.drops)

        return finalised

    def try_with_some_lucky_dust(self):
        return random.randrange(0,2)


    def calculate_fork_outcomes(self, blocks_outcome):
        connotation = Counter(list(o.connotation for o in blocks_outcome)).most_common(3)
        connotation_index = 0

        # random tiebreaker - maybe use lucky dust here
        if len(connotation) > 1 and connotation[0][0] == connotation[1][0]:
            # check if 3rd place is tied as well
            if len(connotation) > 2 and connotation[1][0] == connotation[2][0]:
                connotation_index = random.randrange(0, 3)
            else:
                connotation_index = random.randrange(0, 2)

        connotation = connotation[connotation_index][0]
        return connotation

    def calculate_deepest_branch_from(self, starting_block, block_list):

        depth = 1

        branches = self.traverse_forks([starting_block], block_list)

        while len(branches) != 0:
            branches = self.traverse_forks(branches, block_list)
            depth += 1

        return depth


    def traverse_forks(self, current_list, block_list):

        branches = set()

        for block in current_list:
            for k, v in block.fork.items():
                for block in block_list:
                    if block.id == v.to_id:
                        branches.add(block)

        return branches


    # The overall connotation from the calculated outcomes (outcome_calculator) of one block
    # is fed into the fork which points to the block we should use next.
    def generate_outcome_list(self, block_list):
        results = []

        end_of_blocks = False
        current_block = block_list[0]
        depth = self.calculate_deepest_branch_from(current_block, block_list)

        # start from the first block (might need something here if starting block has to be random)
        while not end_of_blocks:
            # divide the remaining ld by the number of maximum blocks that are still to come
            segment_allotted_ld = self.ld_spend/depth
            # and alter that amount up to + or - the configured variance (%)
            # technically this means that the last event might end up giving away some 'free' ld but that's ok
            ld_variation = random.randrange(0, math.floor(segment_allotted_ld*self.config.ld_variance))
            ld_variation = -ld_variation if random.randrange(0, 2) else ld_variation
            segment_allotted_ld += ld_variation

            # remove it from the pool for next block
            self.ld_spend -= segment_allotted_ld

            print("segment ld")
            print(segment_allotted_ld)
            ld_active = self.can_we_has_ld(segment_allotted_ld, depth)
            if ld_active:
                print("ld on :I")

            current_block_outcomes = list(map(lambda s: (self.outcome_calculator(s, ld_active)),
                                              current_block.segments))
            for outcome in current_block_outcomes:
                results.append(outcome)

            # empty fork means this is the end
            if len(current_block.fork) == 0:
                end_of_blocks = True
            else:
                fork_value = current_block.fork[self.calculate_fork_outcomes(current_block_outcomes)]
                next_block = next((b for b in block_list if b.id == fork_value.to_id), None)
                if next_block is None:
                    raise ReferenceError("No block found (id: {0}). Crumbs probably at fault.".format(fork_value.to_id))
                current_block = next_block

        return results


    def can_we_has_ld(self, segment_allocation, depth):
        return (segment_allocation > self.ld_activation/depth * (random.randrange(0,20)/ 10))


    def get_event(self, event_attributes):
        # see event_patterns desc in docs
        event_data = self.any_of_many(self.crumbs["event_patterns"])

        event = Event(event_attributes, self.build_event_pattern(event_data["blocks"]))

        event_text = ""

        outcome_list = self.generate_outcome_list(event.blocks)
        for outcome in outcome_list:
            event_text = "::: {0} {1} (conn: {2}) :::".format(event_text, outcome.text, outcome.connotation)

        event.calculated_outcomes = outcome_list

        # generate text with @string parameters(crumbs), then fill those in with more generated stuff.
        event.text = self.stuff_the_blanks(event_text[1:])


        return event


    def build_event_pattern(self, blocklist):
        parsed_blocks = []

        random_ints = random.sample(range(1, 10), len(blocklist))
        rnd_sum = sum(random_ints)
        ld_distro = []
        for int in random_ints:
            ld_distro.append(int / rnd_sum * len(blocklist))

        for block in blocklist:
            # a fork is a dictionary with key on the block outcome (+,-,=)
            # and value on the block that needs to follow up + any extra text (optional)
            fork = {}
            for key_pointer in block["fork"]:
                pv = key_pointer["pointer"]
                fork[key_pointer["key"]] = Pointer(pv["to_id"], pv["text"])

            # we need to select one variant out of all the possible ones; variants are not affected by event filters,
            # and unused variants are simply discarded. variants will have different modifier weights
            # (e.g. some variants might be more suitable for certain characters), so that the outcome is never guaranteed
            # and we do not bind the event down to a single set of modifiers.
            variant = block["variants"][random.randrange(0, len(block["variants"]))]
            # each segment has a series of possible outcomes
            segments = []

            for segment in variant:
                # this is where the actual text options are (1 for each outcome)
                outcomes = []
                for outcome in segment["outcomes"]:
                    out = Outcome(outcome["text"], outcome["connotation"], outcome["canvas_id"])
                    if "drops" in outcome:
                        out.drops = outcome["drops"]
                    outcomes.append(out)

                # filters are used to influence which outcome is picked out of the segment
                # based on characteristics, items, conditions, etc.
                filter_data = segment["filtr"]
                ch_mods = []
                for mod in filter_data["char_mod"]:
                    ch_mods.append(Modifier(mod["id"], mod["multi"]))
                filter = Filter(ch_mods, [], [])
                segments.append(Segment(outcomes, filter))

            parsed_blocks.append(SegmentBlock(block["id"], segments, fork))

        return parsed_blocks
