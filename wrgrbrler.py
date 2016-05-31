import argparse
import random
import json
from Manifest import Manifest, Peep, Place, Event
from PIL import Image, ImageFilter

def any_of_many(crumb_list, discard_item = True):
    randomness = random.randrange(0, len(crumb_list))
    item = crumb_list[randomness]
    if discard_item:
        crumb_list.remove(item)
    return item

def drawerer():
    combined = Image.new('RGBA', (100, 300), color=50)

    part1 = Image.open('{0}.png'.format(random.randrange(1, 9)))
    part2 = Image.open('{0}.png'.format(random.randrange(1, 9)))
    part3 = Image.open('{0}.png'.format(random.randrange(1, 9)))

    combined.paste(part1, (0, 0))
    combined.paste(part2, (0, 100))
    combined.paste(part3, (0, 200))

    return combined


def writerer(crumbs, set, subset=None):

    if subset is not None:
        words = crumbs[set][subset]
    else:
        words = crumbs[set]

    wroted = ""

    for key in sorted(words):
        wroted = "{0} {1}".format(wroted, any_of_many(words[key]))

    return wroted[1:]

def main(main_args, crumbs):

    drawed = drawerer()

    manifest = Manifest()

    template = crumbs['templates'][main_args.template]

    #Assuming one event needs only place only - can change later
    places_count = len(template['events'])

    peeps = manifest.peeps
    places = manifest.places
    peeps = []
    places = []

    for x in range(0, int(main_args.peep_count)):
        gender = 'm' if random.randrange(0, 2) else 'f'
        peeps.append(Peep(writerer(crumbs, 'characters', gender), gender))

    for x in range(0, places_count):
        places.append(Place(writerer(crumbs, 'locations')))

    # drawed.show()
    print('{0} went to a {1}, had lunch at a {2}, ended up in a {3}'
          .format(peeps[0].name, places[0].name, places[1].name, places[2].name))


if __name__ == '__main__':
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument('--peep_count')
    argument_parser.add_argument('--template')

    with open('breadcrumbs') as crumbs_file:
        crumbs = json.load(crumbs_file)

    main(argument_parser.parse_args(), crumbs)


