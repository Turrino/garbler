from configparser import ConfigParser
import random
import json
from Manifest import Manifest, Peep, Place, Event
from PIL import Image, ImageFilter


class Wrgrbrler:
    def __init__(self, parsed_crumbs):
        self.crumbs = parsed_crumbs
        #how many event-level patterns can we choose from
        self.event_pattern_range = len(self.crumbs["event_patterns"])

    def any_of_many(self, crumblist, discard_item = True):
        randomness = random.randrange(0, len(crumblist))
        item = crumblist[randomness]
        if discard_item:
            crumblist.remove(item)
        return item

    def stuff_the_blanks(self, parameters_text):
        while parameters_text.find('@') > 0:
            for replacement in self.crumbs["replacements"]:
                parameters_text = parameters_text.replace("@{0}@".format(replacement), self.get_element(replacement))
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
        event = Event(event_attributes)
        pattern = self.crumbs["event_patterns"][(random.randrange(0,self.event_pattern_range))]
        #generate text with @string parameters (see crumbs), then fill those in with more generated stuff.
        event.text = self.stuff_the_blanks(self.writerer(pattern, event.mood))
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


