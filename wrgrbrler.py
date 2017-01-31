import os
import yaml
from builders.Event import Event
from builders.ForkParser import ForkParser
from builders.ModParser import ModParser
from builders.Drawerer import Drawerer
from builders.Garbler import Garbler
from interaction.Chosinator import *
from Manifest import *

files_path = os.path.join(os.path.dirname(__file__), "files")

def yaml_loader(path):
    full_path = files_path
    for name in path:
        full_path = os.path.join(full_path, name)
    with open(full_path, 'r') as yaml_file:
        return yaml.load(yaml_file)

def get_crumbs():
    instructions = yaml_loader(["crumbs_v2"])
    thesaurus_vocabulary = yaml_loader(["thesaurus"])
    block_type_definitions = yaml_loader(["events", "block_type_definitions"])
    story_fundamentals = yaml_loader(["events", "story_fundamentals"])
    context = yaml_loader(["context"])
    story_fundamentals["context"] = context
    drops = yaml_loader(["events", "presets", "drops"])
    attributes = yaml_loader(["events", "presets", "attributes"])
    mods = ModParser.parse_all(yaml_loader(["events", "presets", "mods"]), attributes)

    blocks_dict = {}

    entry_point = block_type_definitions["entry_point"]
    block_type_definitions = block_type_definitions["definitions"]

    for definition in block_type_definitions.keys():
        blocks_dict[definition] = []

    for filename in os.listdir(os.path.join(files_path, "events", "blocks")):
        with open(os.path.join(files_path, "events", "blocks", filename), 'r') as yaml_block:
            block = ForkParser.parse(yaml.load(yaml_block), mods, attributes)
            # todo integrity check: if a block def. has multiple out types, then they must be mapped out in the branches
            for k, v in block_type_definitions[block["type"]].items():
                block[k] = v
            blocks_dict[block["type"]].append(block)

    crumbs = Crumbs(instructions, thesaurus_vocabulary["thesaurus"], thesaurus_vocabulary["vocabulary"],
                    blocks_dict, story_fundamentals, drops, mods, attributes, entry_point)

    return crumbs

def get_garbler(crumbs):
    return Garbler(crumbs, config)


def get_default_garbler():
    return get_garbler(get_crumbs())

def main():
    crumbs = get_crumbs()

    garbler = get_garbler(crumbs)

    event = Event(crumbs, garbler, config["interaction"])
    event.run_to_end()

    drawerer = Drawerer(crumbs)

    drawed = drawerer.combine(event)

    print(event.text)

    drawed.show()

config = yaml_loader(["config_v2"])

if __name__ == '__main__':
    main()


