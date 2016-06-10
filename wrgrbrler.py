from configparser import ConfigParser
import random
import json
from Manifest import Manifest, Peep, Place, Event
from PIL import Image, ImageFilter


class Wrgrbrler:
    def __init__(self, parsed_crumbs):
        self.crumbs = parsed_crumbs

    def any_of_many(self, crumblist, discard_item = True):
        randomness = random.randrange(0, len(crumblist))
        item = crumblist[randomness]
        if discard_item:
            crumblist.remove(item)
        return item

    def writerer(self, crumbset_key, subset=None):

        get = self.any_of_many

        def fetch_subset(words):
            pick = self.any_of_many(words)
            return pick[subset] if type(pick) is list else pick

        if subset is not None:
            get = fetch_subset

        wroted = ""

        crumbset = self.crumbs[crumbset_key]

        for key in sorted(crumbset):
            wroted = "{0} {1}".format(wroted, get(crumbset[key]))

        return wroted[1:]

    def get_peep(self, gender = None):
        if gender is None:
            gender = random.randrange(0, 2)
        return Peep(self.writerer('characters', gender), gender)

    def get_place(self, gender=None):
        return Place(self.writerer('locations'))

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
    places_count = len(template['events'])
    peep_count = int(parser.get('setup', 'peep_count'))

    garbler = Wrgrbrler(crumbs)

    drawed = drawerer()

    manifest = Manifest()

    peeps = manifest.peeps
    places = manifest.places

    for x in range(0, peep_count):
        peeps.append(garbler.get_peep())

    for x in range(0, places_count):
        places.append(garbler.get_place())

    # drawed.show()
    print('{0} went to a {1}, had lunch at a {2}, ended up in a {3}'
          .format(peeps[0].name, places[0].name, places[1].name, places[2].name))
    print('{0} gender is {1}'.format(peeps[0].name, peeps[0].gender, places[1].name, places[2].name))


if __name__ == '__main__':
    main()


