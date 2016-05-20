import argparse
import random
from PIL import Image, ImageFilter

def main(main_args):

    combined = Image.new('RGBA', (100,300), color=50)

    part1 = Image.open("{0}.png".format(random.randrange(1, 9)))
    part2 = Image.open("{0}.png".format(random.randrange(1, 9)))
    part3 = Image.open("{0}.png".format(random.randrange(1, 9)))

    combined.paste(part1, (0, 0))
    combined.paste(part2, (0, 100))
    combined.paste(part3, (0, 200))

    combined.show()


if __name__ == '__main__':
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument('--file')
    argument_parser.add_argument('--file2')

    main(argument_parser.parse_args())

