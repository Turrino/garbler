from configparser import ConfigParser
from collections import Counter
import random
import json
import os
import yaml
import math
from Manifest import *
import subprocess
from contextlib import contextmanager
from PIL import Image, ImageFilter

class Drawerer:

    def __init__(self, canvas_cache):
        if canvas_cache is None:
            self.canvas_cache = self.recreate_cache()
        else:
            self.canvas_cache = canvas_cache

    def combine(self, outcomes):
        combined = Image.new('RGBA', (100, len(outcomes)*100), color=50)

        position = 0

        for outcome in outcomes:
            piece = self.assemble_canvas(outcome)
            combined.paste(piece, (0, position))
            position += 100

        return combined

    def assemble_canvas(self, outcome):
        # to do: assemble all the pieces!
        canvas = self.canvas_cache[outcome.canvas_id]
        img = Image.open(os.path.join('pictures/tiles/background', canvas.background))
        if outcome.ld_sparkle:
            img.paste(Image.open('pictures/ldstar.png'), (90, 1))
        for item in outcome.metadata:
            if item["display"]:
                #item_img = self.transmogrify(item["type_path"], item["keys"])
                item_img = Image.open('pictures/sampletoken.png')
                coords = canvas.overlay[self.channel_to_rgb[item["position"][0]]][item["position"][1]]
                img.paste(item_img, coords)
        return img

    # ask for a type to be created, and the drawerer shall return a picture based on the info provided
    def transmogrify(self, type_path, keys):
        # to do
        return None



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

    def recreate_cache(self):
        Canvasses = {}

        overlays = os.listdir("pictures/tiles/overlay")
        statics = os.listdir("pictures/tiles/static")

        for filename in os.listdir("pictures/tiles/background"):

            overlay_file = filename if filename in overlays else "default_overlay.png"
            overlay = self.get_overlay_metadata(os.path.join("pictures/tiles/overlay", overlay_file))

            static = os.path.join("pictures/tiles/static", filename) if filename in statics else None

            canvas_id = int(filename.replace(".png", ""))

            Canvasses[canvas_id] = Canvas(canvas_id, filename, overlay, static)

        return Canvasses

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