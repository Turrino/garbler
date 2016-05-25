import argparse
import random
import json
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

def writerer(crumbs, set):

    characterInfo = crumbs[set]

    wroted = ""

    for key in sorted(characterInfo):
        wroted = "{0} {1}".format(wroted, any_of_many(characterInfo[key]))

    return wroted[1:]


def main(main_args, crumbs):

    drawed = drawerer()

    character = writerer(crumbs, 'characters')
    place1 = writerer(crumbs, 'locations')
    place2 = writerer(crumbs, 'locations')
    place3 = writerer(crumbs, 'locations')

    # drawed.show()
    print('{0} went to a {1}, had lunch at a {2}, ended up in a {3}'.format(character, place1, place2, place3))



if __name__ == '__main__':
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument('--argumenthere')

    with open('breadcrumbs') as crumbs_file:
        crumbs = json.load(crumbs_file)

    main(argument_parser.parse_args(), crumbs)


