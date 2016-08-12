from configparser import ConfigParser
import random
import json
from Manifest import *
from PIL import Image, ImageFilter


class Wrgrbrler:
    def __init__(self, parsed_crumbs):
        self.crumbs = parsed_crumbs
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

    def get_peep(self, name, gender=None):
        if gender is None:
            gender = random.randrange(0, 2)
        return Peep(name, self.writerer(self.crumbs['characters'], gender), gender)

    def get_place(self, gender=None):
        return Place(self.writerer(self.crumbs['locations']))

    def get_element(self, category):
        return self.writerer(self.crumbs[category], -1)

    def get_event(self, event_attributes):
        # see event_patterns desc in docs
        blocks = self.crumbs["event_patterns"][(random.randrange(0,self.event_pattern_range))]

        event = Event(event_attributes, blocks)

        <<<>>>>># pass the right stuff to writerer, not blocks

        #generate text with @string parameters (see crumbs), then fill those in with more generated stuff.
        event.text = self.stuff_the_blanks(self.writerer())
        # random subset would be : [....] self.writerer(pattern, random.randrange(0, 3))
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

def build_event_patterns(crumbs):
    events_patterns = []
    for raw_event in crumbs['event_patterns']:
        segment_blocks = []
        for block in raw_event["blocks"]:
            #for is a dictionary with key on the block outcome (+,-,=)
            #and value on the block that needs to follow up + any extra text (optional)
            fork = {}
            for key_pointer in block["fork"]:
                pv = key_pointer["pointer"]
                fork[key_pointer["key"]] = Pointer(pv["to_id"], pv["text"])

            #each segment has a series of possible outcomes
            segments = []
            for segment in block["segments"]:
                # this is where the actual text options are (1 for each outcome)
                outcomes = []
                for outcome in segment["outcomes"]:
                    outcomes.append(Outcome(outcome["text"], outcome["connotation"]))

                # filters are used to influence which outcome is picked out of the segment
                # based on characteristics, items, conditions, etc.
                filter_data = segment["filter"]
                ch_mods = []
                for mod in filter_data["char_mod"]:
                    ch_mods.append(Modifier(mod["id"], mod["mods"]))

                    ### TO DO: implement item and lucky (and any other needed) mods.
                    ###  right now we don't even parse them because cba
                filter = Filter(ch_mods, [], [])
                segments.append(Segment(outcomes, filter))

            segment_blocks.append(SegmentBlock(block["id"], segments, fork))
        # one list of segment blocks can be used by one event
        events_patterns.append(segment_blocks)

    return events_patterns

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
    peep_count = int(parser.get('setup', 'peep_count'))
    peep_names = str.split(parser.get('setup', 'peep_names'), ',')

    if peep_count != len(peep_names):
        raise ValueError('Number of peeps ({0}) and number of peep names ({1}) provided does not match, fix the config.'
              .format(peep_count, len(peep_names)))

    crumbs.events_patterns = build_event_patterns(crumbs)

    garbler = Wrgrbrler(crumbs)

    drawed = drawerer()

    manifest = Manifest()

    peeps = manifest.peeps
    places = manifest.places
    events = manifest.events

    for x in range(0, peep_count):
        peeps.append(garbler.get_peep(peep_names[x]))

    for x in range(0, events_count):
        places.append(garbler.get_place())
        # put back once we have enough crumbs not to crash
        # get event of the type needed at this index by the template
        #events.append(garbler.get_event(template['events'][x]))

    ##remove later
    events.append(garbler.get_event(template['events'][1]))


    # drawed.show()
    print('{0}, the {1}, went to a {2}, had lunch at a {3}, ended up in a {4}'
          .format(peeps[0].name, peeps[0].desc, places[0].name, places[1].name, places[2].name))
    print('{0} gender is {1}'.format(peeps[0].desc, peeps[0].gender, places[1].name, places[2].name))
    for event in events:
        print('event: {0} {1}: {2}'.format(event.type, event.mood, event.text))


if __name__ == '__main__':
    main()


