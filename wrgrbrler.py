import os
import yaml
from builders.ForkParser import ForkParser
from builders.ModParser import ModParser
from builders.Drawerer import Drawerer
from builders.Garbler import Garbler
from Manifest import *

files_path = os.path.join(os.path.dirname(__file__), "files")

def yaml_loader(path):
    full_path = files_path
    for name in path:
        full_path = os.path.join(full_path, name)
    with open(full_path, 'r') as yaml_file:
        return yaml.load(yaml_file)

def get_default_garbler():
    config = yaml_loader(["config_v2"])

    instructions = yaml_loader(["crumbs_v2"])
    thesaurus_vocabulary = yaml_loader(["thesaurus"])
    block_type_definitions = yaml_loader(["events", "block_type_definitions"])
    story_fundamentals = yaml_loader(["events", "story_fundamentals"])
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
            # todo if a block def. has multiple out types, then they must be mapped out in the branches
            for k, v in block_type_definitions[block["type"]].items():
                block[k] = v
            blocks_dict[block["type"]].append(block)

    crumbs = Crumbs(instructions, thesaurus_vocabulary["thesaurus"], thesaurus_vocabulary["vocabulary"],
                    blocks_dict, story_fundamentals, drops, mods, attributes, entry_point)

    peep_config = config["peep"]
    garbler_config = config["garbler"]

    # todo remove once we have data coming from the proper source
    peep = Peep(peep_config["name"], peep_config["attribs"], peep_config["gender"])
    peep.ld = garbler_config["starting_ld"] - garbler_config["ld_spend"]

    return Garbler(crumbs, peep, garbler_config)


def main():
    garbler = get_default_garbler()

    event = garbler.get_event()

    drawerer = Drawerer()

    drawed = drawerer.combine(event)

    drawed.show()

    if garbler.ld_spend > 0:
        print("looks like there's some ld left.. ld: {0}".format(garbler.ld_spend))

    manifest = Manifest(peep, places, [event])

    print('{0}, the {1}, went to a {2}, had lunch at a {3}, ended up in a {4}'
          .format(peep.name, peep.desc, places[0].name, places[1].name, places[2].name))
    print('{0} gender is {1}. lucky dust: {2}'
          .format(peep.desc, peep.gender, peep.ld))

    print('event: {0} {1}: {2}'.format(event.type, event.mood, event.text))

    print('Loot: ')
    for item in peep.items:
        print(' - {0}; type: {1}; durability: {2}; attribute: {3}'
              .format(item.name, item.type, item.durability, item.print_attributes()))

if __name__ == '__main__':
    main()


