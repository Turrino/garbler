import random
import os
import yaml
from Manifest import *
from contextlib import contextmanager
from builders.CustomFilters import CustomFilters
from PIL import Image, ImageFilter
from Utils import Utils

class Drawerer:
    def __init__(self, crumbs, canvas_cache=None):
        self.crumbs = crumbs
        self.canvas_height = 0
        self.canvas_width = 0
        if canvas_cache is None:
            self.canvas_cache = self.recreate_cache()
        else:
            self.canvas_cache = canvas_cache
        self.asset_names = os.listdir(self.assets)
        self.skeleton_names = os.listdir(self.skeletons)
        self.elements_cache = {}

    def combine(self, event):
        combined = Image.new('RGBA', (self.canvas_width, len(event.tracker)*self.canvas_height), color=50)

        position = 0

        for outcome in event.tracker:
            piece = self.assemble_canvas(outcome)
            combined.paste(piece, (0, position))
            position += self.canvas_height

        return combined

    def assemble_canvas(self, outcome):
        # to do: assemble all the pieces!
        canvas = self.canvas_cache[outcome["canvas"]]
        img = Image.open(os.path.join('pictures/tiles/background', canvas.background))
        #todo redo ld distro
        # if outcome.ld_sparkle:
        #     img.paste(Image.open('pictures/ldstar.png'), (90, 1))
        for itemlist in outcome["meta"]:
            for item in itemlist:
                if item["display"]:
                    if item["cache_id"] is not None:
                        if item["cache_id"] in self.elements_cache:
                            return self.elements_cache["cache_id"]

                    item_img = self.transmogrify(item["type"], item["keys"])
                    # overlay channel (if not specified, use one at random)
                    if len(item["position"]) == 2:
                        channel = self.channel_to_rgb[item["position"][0]]
                    else:
                        channel = Utils.any_of_many(list(canvas.overlay.keys()), False)
                    # available slots for that channel
                    sequence = item["position"][1] if len(item["position"]) == 2 else 0
                    coords = canvas.overlay[channel][sequence]
                    # make sure we don't use an overlay point twice
                    canvas.overlay[channel].pop(sequence)
                    # remove channel if it has no more points
                    if not len(canvas.overlay[channel]):
                        canvas.overlay.pop(channel)
                    img.paste(item_img, coords)

                    if item["cache_id"] is not None:
                        self.elements_cache["cache_id"] = img
        return img

    # ask for a type to be created, and the drawerer shall return a picture based on the info provided
    def transmogrify(self, crumb_type, keys):
        skeleton = self.get_skeleton(crumb_type, True)
        skeleton_base = Image.open(os.path.join(self.skeletons, skeleton + self.extension))
        skeleton_overlay = self.overlay_to_list(self.get_overlay_metadata(
            os.path.join(self.skeletons, skeleton + self.overlay_ext)))

        assets = self.get_assets(keys)

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

    def get_skeleton(self, crumb_type, use_potato=False):
        # path list is ordered as: root > more specific nested levels
        if crumb_type + self.extension in self.skeleton_names:
            return crumb_type
        elif crumb_type in self.crumbs.instructions_map.keys():
            path = list(reversed(self.crumbs.instructions_map[crumb_type]))
            if len(path) != 0:
                for level in path:
                    expected_filename = level + self.extension
                    if expected_filename in self.skeleton_names:
                        return level

        if use_potato:  # if we don't have even the most generic type
            return self.potato_token
        else:
            raise ValueError("descriptive error here")

    def get_assets(self, keys):
        available_assets = []

        def find_asset(type_key):
            # could be either a png, or a yaml file
            expected_filename = type_key + self.extension
            if type_key in self.asset_names:
                available_assets.append(self.deyamlify(os.path.join(self.assets, type_key)))
                return True
            if expected_filename in self.asset_names:
                available_assets.append(expected_filename)
                return True
            return False

        # todo: maybe map this in advance if there is the need to
        for key in keys:
            found = find_asset(key)
            if not found and key in self.crumbs.thesaurus_map.keys():
                path = self.crumbs.thesaurus_map[key]
                if len(path) != 0:
                    path = list(reversed(path))  # start from the most specific
                    for level in path:
                        if find_asset(level):
                            break  # make sure we don't get more than one

        if len(available_assets) == 0:
            available_assets.append(self.potato_token + self.extension)

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
    files_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "files", "pictures")
    tiles = os.path.join(files_path, "tiles")
    skeletons = os.path.join(files_path, "skeletons")
    assets = os.path.join(files_path, "assets")
    backgrounds = os.path.join(tiles, "background")
    overlays = os.path.join(tiles, "overlay")
    static = os.path.join(tiles, "static")
    default_overlay = "default_overlay.png"
    extension = ".png"
    overlay_ext = ".o.png"
    potato_token = "_potato"

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