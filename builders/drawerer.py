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
    def __init__(self, metadata):
        if metadata is None:
            self.metadata = self.recreate_metadata()
        else:
            self.metadata = metadata

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
        img = Image.open(os.path.join('pictures/tiles/background', self.metadata[outcome.canvas_id].background))
        if outcome.ld_sparkle:
            img.paste(Image.open('pictures/ldstar.png'), (90, 1))
        return img


    def get_overlay_metadata(self, overlay_image):

        overlay = Image.open(overlay_image)
        # to do parse metadata
        return [1,2,3]

    def recreate_metadata(self):
        Canvasses = {}

        overlays = os.listdir("pictures/tiles/overlay")
        statics = os.listdir("pictures/tiles/static")
        overlay = "pictures/tiles/overlay/default_overlay.png"

        for filename in os.listdir("pictures/tiles/background"):
            static = None
            if filename in overlays:
                overlay = self.get_overlay_metadata(os.path.join("pictures/tiles/overlay", filename))
            if filename in statics:
                static = os.path.join("pictures/tiles/static", filename)

            canvas_id = int(filename.replace(".png", ""))
            Canvasses[canvas_id] = Canvas(canvas_id, filename, overlay, static)

        return Canvasses





@contextmanager
def cd(newdir):
    prevdir = os.getcwd()
    os.chdir(os.path.join(os.getcwd(), newdir))
    try:
        yield
    finally:
        os.chdir(prevdir)