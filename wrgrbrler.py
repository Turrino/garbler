import argparse
from PIL import Image, ImageFilter

def main(main_args):
    try:
        original = Image.open("1.png")
        blurred = original.filter(ImageFilter.BLUR)

        original.show()
        blurred.show()
    except:
        print("Unable to load image")





if __name__ == '__main__':
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument('--file')
    argument_parser.add_argument('--file2')

    main(argument_parser.parse_args())

