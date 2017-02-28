import os
import yaml
from builders.Event import Event
from builders.Fetcher import Fetcher
from builders.Drawerer import Drawerer
from builders.ModParser import ModParser
from builders.ForkParser import ForkParser
from input.Modes import Modes
from Inspector import Inspector
from Crumbs import *

class Garbler:
    def __init__(self, config_path, load_context=False):
        self.config = self.yaml_loader(config_path)
        self.files_path = self.config["files_folder"]
        self.crumbs = self.get_crumbs()
        self.fetcher = Fetcher(self.crumbs)
        self.drawerer = Drawerer(self.files_path, self.crumbs)
        self.event = Event(self.crumbs, self.fetcher)
        if load_context:
            with open(os.path.join(self.files_path, "context"), 'r') as context_file:
                self.add_context(context_file)

    def run_to_end_auto(self, draw=False):
        choice = None
        while not self.event.complete:
            fork = self.event.step(choice)
            if type(fork) is Choice:
                choice = Utils.any_of_many(fork.options, False).to
        if draw:
            self.event.drawed = self.drawerer.combine(self.event)
        return self.event

    def get_current_canvas(self):
        return self.drawerer.get_canvas_for(self.event.tracking_element)

    def get_new_event(self, restore_crumbs=False):
        if restore_crumbs:
            self.crumbs = self.get_crumbs()
        event = Event(self.crumbs, self.fetcher)
        return event

    def yaml_loader(self, path):
        if type(path) is list:
            full_path = self.files_path
            for name in path:
                full_path = os.path.join(full_path, name)
        else:
            full_path = path
        with open(full_path, 'r') as yaml_file:
            return yaml.load(yaml_file)

    # for integrity checks, have these loaded all at once,
    # then check that all the special parameters in the blocks can be fetched from something in here
    def add_context(self, instructions):
        context_input = yaml.load(instructions)

        def transform_function(parameter_text):
            return Utils.stuff_the_blanks(parameter_text, self.crumbs.story_cache, self.fetcher.get_element)

        #todo document usage of add_context and the special instruction $
        def transform_filter(item):
            return item[0] == '$'

        parsed_instructions = Utils.transform_all(context_input, transform_function, transform_filter)

        #todo check that we're not overwriting anything!!
        if "identifier" in parsed_instructions.keys():
            self.crumbs.story_cache[parsed_instructions["identifier"]] = parsed_instructions
        else:
            for key, value in parsed_instructions.items():
                self.crumbs.story_cache[key] = value

    def get_crumbs(self, inspect=False):
        instructions = self.yaml_loader(["crumbs"])
        thesaurus_vocabulary = self.yaml_loader(["thesaurus"])
        block_type_definitions = self.yaml_loader(["events", "block_type_definitions"])
        story_fundamentals = self.yaml_loader(["events", "story_fundamentals"])
        primers = {}
        for filename in os.listdir(os.path.join(self.files_path, "events", "primers")):
            with open(os.path.join(self.files_path, "events", "primers", filename), 'r') as yaml_primer:
                primers[filename] = yaml.load(yaml_primer)
        drops = self.yaml_loader(["events", "presets", "drops"])
        attributes = self.yaml_loader(["events", "presets", "attributes"])
        mods = ModParser.parse_all(self.yaml_loader(["events", "presets", "mods"]), attributes)

        blocks_dict = {}

        entry_point = block_type_definitions["entry_point"]
        block_type_definitions = block_type_definitions["definitions"]

        for definition in block_type_definitions.keys():
            blocks_dict[definition] = []

        for filename in os.listdir(os.path.join(self.files_path, "events", "blocks")):
            with open(os.path.join(self.files_path, "events", "blocks", filename), 'r') as yaml_block:
                block = ForkParser.parse(yaml.load(yaml_block), mods, attributes)
                # todo integrity check: if a block def. has multiple out types, then they must be mapped out in the branches
                for k, v in block_type_definitions[block["type"]].items():
                    block[k] = v
                blocks_dict[block["type"]].append(block)

        crumbs = Crumbs(instructions, thesaurus_vocabulary["thesaurus"], thesaurus_vocabulary["vocabulary"],
                        blocks_dict, story_fundamentals, primers, drops, mods, attributes, entry_point)

        if inspect:
            Inspector.run_all_checks(crumbs)

        return crumbs



