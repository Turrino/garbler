from configparser import ConfigParser
from collections import Counter
import random
import os
import yaml
from Manifest import *
from contextlib import contextmanager
from builders.CustomFilters import CustomFilters
from PIL import Image, ImageFilter

class Drawerer:

    def __init__(self, canvas_cache):
        self.canvas_height = 0
        self.canvas_width = 0
        if canvas_cache is None:
            self.canvas_cache = self.recreate_cache()
        else:
            self.canvas_cache = canvas_cache
        self.asset_names = os.listdir(self.assets)
        self.skeleton_names = os.listdir(self.skeletons)

    def combine(self, outcomes):
        combined = Image.new('RGBA', (self.canvas_width, len(outcomes)*self.canvas_height), color=50)

        position = 0

        for outcome in outcomes:
            piece = self.assemble_canvas(outcome)
            combined.paste(piece, (0, position))
            position += self.canvas_height

        return combined

    def assemble_canvas(self, outcome):
        # to do: assemble all the pieces!
        canvas = self.canvas_cache[outcome.canvas_id]
        img = Image.open(os.path.join('pictures/tiles/background', canvas.background))
        if outcome.ld_sparkle:
            img.paste(Image.open('pictures/ldstar.png'), (90, 1))
        for item in outcome.metadata:
            if item["display"]:
                item_img = self.transmogrify(item["type_path"], item["keys"])
                coords = canvas.overlay[self.channel_to_rgb[item["position"][0]]][item["position"][1]]
                img.paste(item_img, coords)
        return img

    # ask for a type to be created, and the drawerer shall return a picture based on the info provided
    def transmogrify(self, type_path, keys):
        skeleton = self.get_skeleton(type_path)
        assets = self.get_assets(keys)

        skeleton_base = Image.open(os.path.join(self.skeletons, skeleton + self.extension))
        skeleton_overlay = self.overlay_to_list(self.get_overlay_metadata(
            os.path.join(self.skeletons, skeleton + self.overlay_ext)))

        # to do: introduce some integrity checks on the data so that this never happens.
        # but, if we still end up in this situation, do not crash, generate random overlay data instead
        if len(assets) > len(skeleton_overlay):
            print(format("Warning: not enough overlay points ({0}) for type {1}. Generating random ones.",
                         len(skeleton_overlay), keys))
            for i in range (len(skeleton_overlay), len(assets)):
                skeleton_overlay.append((random.randrange(0, skeleton_base.size[0]),
                                        random.randrange(0, skeleton_base.size[1])))

        filters = []

        for i in range(0, len(assets)):
            if type(assets[i]) is str: # then it's the file path of an asset
                asset_img = Image.open(os.path.join(self.assets, assets[i]))
                # [0] is for the first coords tuple in the channel
                # we probably want only one set of coordinates for each channel in skeleton overlays, tbc)
                skeleton_base.paste(asset_img, skeleton_overlay[i][0])
            elif type(assets[i]) is list:
                filters = filters + assets[i]
            # and if it's not one of the above, don't do anything - the skeleton base stays as is

        if len(filters):
            modifications = CustomFilters(filters, skeleton_base)
            skeleton_base = modifications.apply_all()

        return skeleton_base



    def get_skeleton(self, type_path):
        type_lookup = list(reversed(type_path))

        for key in type_lookup:
            expected_filename = key + self.extension
            if expected_filename in self.skeleton_names:
                return key  # to do: allow a file to have variants, especially skeletons/overlays

    def get_assets(self, keys):
        available_assets = []

        for key in keys:
            # could be either a png, or a yaml file
            expected_filename = key + self.extension
            if key in self.asset_names:
                available_assets.append(self.deyamlify(os.path.join(self.assets, key)))
            if expected_filename in self.asset_names:
                available_assets.append(expected_filename)
            else:
                available_assets.append(None)

        return available_assets

    def deyamlify(self, file_path):
        with open(file_path, 'r') as file:
            instructions = yaml.load(file)
            # for now, the only allowed thing here is a list of filters from CustomFilters (the yaml file tells us which)
            # can be expanded with more custom stuff (e.g. load new instructions through yaml)
        return instructions


    def get_overlay_metadata(self, overlay_image):
        parsed_overlay = {}

        for ch in self.channels:
            parsed_overlay[ch] = []

        overlay = Image.open(overlay_image)
        pixels = overlay.load()
        for x in range(0, overlay.width):
            for y in range(0, overlay.height):
                if pixels[x,y] != (0,0,0):
                    if pixels[x,y] in self.channels:
                        parsed_overlay[pixels[x,y]].append((x,y))
                    else:
                        raise ValueError("found a pixel with unrecognized RGB overlay value")

        return parsed_overlay

    def overlay_to_list(self, overlay):
        o_list = []
        rgb_channels = overlay.keys()

        for i in range(1, len(self.channels)+1):
            rgb_code = self.channel_to_rgb[i]
            if rgb_code in rgb_channels:
                o_list.append(overlay[rgb_code])

        return o_list


    def recreate_cache(self):
        Canvasses = {}

        overlays_names = os.listdir(self.overlays)
        static_names = os.listdir(self.static)
        background_names = os.listdir(self.backgrounds)

        sample = Image.open(os.path.join(self.backgrounds, background_names[0]))

        self.canvas_height = sample.size[1]
        self.canvas_width = sample.size[0]

        for filename in background_names:

            overlay_file = filename if filename in overlays_names else self.default_overlay
            overlay = self.get_overlay_metadata(os.path.join(self.overlays, overlay_file))

            static = os.path.join(self.static, filename) if filename in static_names else None

            canvas_id = int(filename.replace(self.extension, ""))

            Canvasses[canvas_id] = Canvas(canvas_id, filename, overlay, static)

        if not self.canvas_height or not self.canvas_width:
            raise ValueError("The reference sample for canvas has a weird size, check {0}".format(background_names[0]))

        return Canvasses

    # filepaths
    extension = ".png"
    overlay_ext = ".o.png"
    backgrounds = "pictures/tiles/background"
    overlays = "pictures/tiles/overlay"
    default_overlay = "default_overlay.png"
    static = "pictures/tiles/static"
    skeletons = "pictures/skeletons"
    assets = "pictures/assets"

    # overlay colours
    ch1 = (255, 0, 0) #red
    ch2 = (255, 170, 0) # orange
    ch3 = (212, 255, 0) # lime
    ch4 = (0, 255, 85) # green
    ch5 = (0, 255, 255) # cyan
    ch6 = (0, 85, 255) # blue
    ch7 = (85, 0, 255) # violet
    ch8 = (255, 0, 255) # pink

    channels = [ch1, ch2, ch3, ch4, ch5, ch6, ch7, ch8]
    channel_to_rgb = { 1:(255, 0, 0),2:(255, 170, 0),3:(212, 255, 0),4:(0, 255, 85),5:(0, 255, 255),6:(0, 85, 255),7:(85, 0, 255),8:(255, 0, 255) }

@contextmanager
def cd(newdir):
    prevdir = os.getcwd()
    os.chdir(os.path.join(os.getcwd(), newdir))
    try:
        yield
    finally:
        os.chdir(prevdir)