import os
import yaml
from builders.Event import Event
from builders.Fetcher import Fetcher
from builders.Drawerer import Drawerer
from builders.CrumbUtils import *
from builders.Replacements import *
from builders.ForkParser import ForkParser
import uuid
from Inspector import Inspector
from Crumbs import *

class Garbler:
    def __init__(self, files_path, load_context=False, cache_directory=None):
        self.files_path = files_path
        self.config = self.yaml_loader(os.path.join(files_path, 'config'))
        self.crumbs = self.get_crumbs()
        self.fetcher = Fetcher(self.crumbs)
        self.drawerer = Drawerer(self.files_path, self.crumbs)
        self.event = self.get_new_event()
        if load_context:
            with open(os.path.join(self.files_path, "context"), 'r') as context_file:
                self.add_context(context_file)
        self.cache_directory = cache_directory

    def run_to_end_auto(self, draw=False):
        choice = None
        while not self.event.complete:
            fork = self.event.step(choice)
            if type(fork) is Choice:
                choice = any_of_many(fork.options, False).to
        if draw:
            self.event.drawed = self.drawerer.combine(self.event)
        return self.event

    def get_current_canvas(self):
        return self.drawerer.get_canvas_for(self.event.tracking_element)

    def get_new_event(self, restore_crumbs=False):
        self.session_cache = {"images": []}
        if restore_crumbs:
            self.crumbs = self.get_crumbs()
        event = Event(self.crumbs, self.fetcher)
        return event


    # Will crash if there is no cache directory. Make a version that will work without it, if needed
    def step(self, pointer=None):
        fork = self.event.step(pointer)
        choices = []
        image = self.get_current_canvas()
        img_name = "{0}.png".format(uuid.uuid4())
        self.session_cache["images"].append(img_name)
        image.save(os.path.join(self.cache_directory, img_name), "PNG")
        if type(fork) is Choice:
            complete = False
            choices = fork.options
            event_text = self.event.get_text_batch()
        elif self.event.complete:
            complete = True
            event_text = self.event.text
            img_name = "f__{}.png".format(uuid.uuid4())
            cached_images = [os.path.join(self.cache_directory, img) for img in self.session_cache["images"]]
            merged_images = self.drawerer.join(cached_images)
            merged_images.save(os.path.join(self.cache_directory, img_name), "PNG")
        else:
            raise ValueError("cba")

        self.session_cache["step"] = {
            "complete": complete,
            "choices": choices,
            "text": event_text,
            "image": img_name
        }
        return self.session_cache["step"]

    def yaml_loader(self, path):
        if type(path) is list:
            full_path = self.files_path
            for name in path:
                full_path = os.path.join(full_path, name)
        else:
            full_path = path
        with open(full_path, 'r') as yaml_file:
            return yaml.load(yaml_file)

    def add_context(self, instructions):
        context_input = yaml.load(instructions)
        parsed_instructions = transform_all(context_input, transform_function, transform_filter)
        #todo check that we're not overwriting anything!!
        if "identifier" in parsed_instructions.keys():
            self.crumbs.story_cache[parsed_instructions["identifier"]] = parsed_instructions
        else:
            for key, value in parsed_instructions.items():
                self.crumbs.story_cache[key] = value

    def get_crumbs(self, inspect=False):
        instructions = []
        for filename in os.listdir(os.path.join(self.files_path, "crumbs")):
            with open(os.path.join(self.files_path, "crumbs", filename), 'r') as yaml_crumbs:
                read_crumb_package(yaml.load(yaml_crumbs), instructions)

        thesaurus_vocabulary = self.yaml_loader(["thesaurus"])
        blocks_dict = {}
        for filename in os.listdir(os.path.join(self.files_path, "events", "blocks")):
            with open(os.path.join(self.files_path, "events", "blocks", filename), 'r') as yaml_block:
                block = ForkParser(yaml.load(yaml_block)).update_block()
                if block["type"] in blocks_dict.keys():
                    blocks_dict[block["type"]].append(block)
                else:
                    blocks_dict[block["type"]] = [block]
        crumbs = Crumbs(instructions, thesaurus_vocabulary["thesaurus"], thesaurus_vocabulary["vocabulary"],
                        blocks_dict, None)
        if inspect:
            Inspector.run_all_checks(crumbs)
        return crumbs



