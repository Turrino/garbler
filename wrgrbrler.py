import argparse
import random
import json
from PIL import Image, ImageFilter

def any_of_many(crumb_list):
    return crumb_list[random.randrange(0, len(crumb_list))]

def drawerer():
    combined = Image.new('RGBA', (100, 300), color=50)

    part1 = Image.open('{0}.png'.format(random.randrange(1, 9)))
    part2 = Image.open('{0}.png'.format(random.randrange(1, 9)))
    part3 = Image.open('{0}.png'.format(random.randrange(1, 9)))

    combined.paste(part1, (0, 0))
    combined.paste(part2, (0, 100))
    combined.paste(part3, (0, 200))

    return combined

def writerer(crumbs):

    characterInfo = crumbs['charatest']

    wroted = '{0} {1} {2}'.format(any_of_many(characterInfo['part1']),
                                  any_of_many(characterInfo['part2']),
                                  any_of_many(characterInfo['part3']))

    return wroted


def main(main_args, crumbs):

    drawed = drawerer()

    wroted = writerer(crumbs)

    drawed.show()
    print(wroted)



if __name__ == '__main__':
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument('--argumenthere')

    with open('breadcrumbs') as crumbs_file:
        crumbs = json.load(crumbs_file)

    main(argument_parser.parse_args(), crumbs)

