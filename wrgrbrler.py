from configparser import ConfigParser
import random
import json
from Manifest import *
from PIL import Image, ImageFilter


class Wrgrbrler:
    def __init__(self, parsed_crumbs, peep, random_mod):
        self.crumbs = parsed_crumbs
        self.peep = peep
        peep.desc = self.writerer(self.crumbs['characters'], peep.gender)
        self.random_mod = random_mod
        #how many event-level patterns can we choose from
        self.event_pattern_range = len(self.crumbs['event_patterns'])

    def any_of_many(self, crumblist, discard_item = True):
        randomness = random.randrange(0, len(crumblist))
        item = crumblist[randomness]
        if discard_item:
            crumblist.remove(item)
        return item

    def stuff_the_blanks(self, parameters_text):
        while parameters_text.find('@') > 0:
            for replacement in self.crumbs['replacements']:
                #the last parameter limits replacements to 1 so that if the text has two items in the same category
                #we don't end up with duplicates. if an item is speshul and needs to be repeated, then make a diff method
                parameters_text = parameters_text.replace("@{0}@".format(replacement), self.get_element(replacement), 1)
        return parameters_text

    def writerer(self, crumbset, subset=None):
        fetch_crumb = self.any_of_many

        #We use this only if a subset parameter (mood, gender...) is passed in, in order to access
        #Then check if the selected element is a list - some elements are universal and do not have a subset
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

    def outcome_calculator(self, segment):
        outcome_tally = []

        # 1 is the basic value for an outcome to happen
        # the higher, the more likelyhood of it being picked
        # can go below 1 but not below 0
        for outcome in segment.outcomes:
            outcome_tally.append(1)

        for mod in segment.filtr.char_mod:
            if mod.id in self.peep.attributes:
                #each multiplier is a list of two integers, the first represents the outcome we want to affect
                #and the second is the actual likelyhood multiplier value (which can be more or less than 1)
                for multiplier in mod.multipliers:
                    outcome_tally[multiplier[0]-1] = outcome_tally[multiplier[0]-1]*multiplier[1]

        top_tally = max(outcome_tally)


        random_modifier = top_tally * self.random_mod
        outcome_tally = list(map(lambda o: (o - (random.randrange(0, random_modifier*100))/100), outcome_tally))
        top_tally = max(outcome_tally)

        selected_outcome = [i for i, j in enumerate(outcome_tally) if j == top_tally]

        index = 0

        if len(selected_outcome) != 1:
            index = random.randrange(0, len(selected_outcome))

        return segment.outcomes[int(selected_outcome[index])]

    def get_event(self, event_attributes):
        # see event_patterns desc in docs
        event_data = self.any_of_many(self.crumbs["event_patterns"])

        event = Event(event_attributes, build_event_pattern(event_data["blocks"]))

        event_text = ""

        for block in event.blocks:
            for segment in block.segments:
                #to do: make use of the outcome connotation, not just the text (implement forks)
                event_text = "{0} {1}".format(event_text, self.outcome_calculator(segment).text)

        # generate text with @string parameters(crumbs), then fill those in with more generated stuff.
        event.text = self.stuff_the_blanks(event_text[1:])

        return event


def drawerer():
    combined = Image.new('RGBA', (100, 300), color=50)

    part1 = Image.open('{0}.png'.format(random.randrange(1, 9)))
    part2 = Image.open('{0}.png'.format(random.randrange(1, 9)))
    part3 = Image.open('{0}.png'.format(random.randrange(1, 9)))

    combined.paste(part1, (0, 0))
    combined.paste(part2, (0, 100))
    combined.paste(part3, (0, 200))

    return combined

def build_event_pattern(blocklist):
    parsed_blocks = []
    for block in blocklist:
        #for is a dictionary with key on the block outcome (+,-,=)
        #and value on the block that needs to follow up + any extra text (optional)
        fork = {}
        for key_pointer in block["fork"]:
            pv = key_pointer["pointer"]
            fork[key_pointer["key"]] = Pointer(pv["to_id"], pv["text"])

        #we need to select one variant out of all the possible ones; variants are not affected by event filters,
        #and unused variants are simply discarded. variants will have different modifier weights
        #(e.g. some variants might be more suitable for certain characters), so that the outcome is never guaranteed
        #and we do not bind the event down to a single set of modifiers.
        variant = block["variants"][random.randrange(0, len(block["variants"]))]
        # each segment has a series of possible outcomes
        segments = []

        for segment in variant:
            # this is where the actual text options are (1 for each outcome)
            outcomes = []
            for outcome in segment["outcomes"]:
                outcomes.append(Outcome(outcome["text"], outcome["connotation"]))

            # filters are used to influence which outcome is picked out of the segment
            # based on characteristics, items, conditions, etc.
            filter_data = segment["filtr"]
            ch_mods = []
            for mod in filter_data["char_mod"]:
                ch_mods.append(Modifier(mod["id"], mod["multi"]))

                ### TO DO: implement item and lucky (and any other needed) mods.
                ###  right now we don't even parse them because cba
            filter = Filter(ch_mods, [], [])
            segments.append(Segment(outcomes, filter))

        parsed_blocks.append(SegmentBlock(block["id"], segments, fork))

    return parsed_blocks

def main():

    parser = ConfigParser()
    parser.read('../config')

    crumbs = None
    with open('breadcrumbs') as crumbs_file:
        crumbs = json.load(crumbs_file)

    template_name = parser.get('setup', 'template')
    template = crumbs['templates'][template_name]
    # Assuming one event needs only place only - can change later
    events_count = len(template['events'])

    #this is a multiplier, the higher the value = more random events, less influence by modifiers
    rm = float(parser.get('setup', 'random_mod'))

    #to do - remove this later, input will come from actual character(s)
    #also for now we don't need multiple, stick to one
    peep_name = parser.get('setup', 'peep_name')
    peep_gender = int(parser.get('setup', 'peep_gender'))
    peep_attrib = {}
    for kvp in str.split(parser.get('setup', 'peep_attrib'), ';'):
        split_kvp = str.split(kvp, ',')
        peep_attrib[split_kvp[0]] = split_kvp[1]

    peep = Peep(peep_name, peep_attrib, peep_gender)
    places = []
    events = []

    garbler = Wrgrbrler(crumbs, peep, rm)

    drawed = drawerer()

    for x in range(0, events_count):
        places.append(garbler.get_place())
        # put back once we have enough crumbs not to crash
        # get event of the type needed at this index by the template
        #events.append(garbler.get_event(template['events'][x]))

    ##remove later
    events.append(garbler.get_event(template['events'][1]))

    manifest = Manifest(peep, places, events)

    # drawed.show()
    print('{0}, the {1}, went to a {2}, had lunch at a {3}, ended up in a {4}'
          .format(peep.name, peep.desc, places[0].name, places[1].name, places[2].name))
    print('{0} gender is {1}'.format(peep.desc, peep.gender, places[1].name, places[2].name))
    for event in events:
        print('event: {0} {1}: {2}'.format(event.type, event.mood, event.text))


if __name__ == '__main__':
    main()


