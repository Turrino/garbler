from configparser import ConfigParser
from collections import Counter
import random
import json
import os
import yaml
from builders.drawerer import Drawerer
from builders.garbler import Garbler
import math
from Manifest import *
from PIL import Image, ImageFilter


def main():
    with open("config_v2", 'r') as yaml_config:
        configs = yaml.load(yaml_config)

    with open("crumbs_v2", 'r') as yaml_crumbs:
        crumbs = yaml.load(yaml_crumbs)

    with open("thesaurus", 'r') as yaml_thesaurus:
        thesaurus_vocabulary = yaml.load(yaml_thesaurus)

    peep_config = configs["peep"]
    garbler_config = configs["garbler"]

    crumbs['event_patterns'] = []

    for filename in os.listdir("events"):
        with open(os.path.join("events", filename), 'r') as event:
            crumbs['event_patterns'].append(yaml.load(event))

    template_name = garbler_config.template
    template = crumbs['templates'][template_name]
    # Assuming one event needs only place only - can change later
    events_count = len(template['events'])

    #remove once we have data coming from the proper source
    peep = Peep(peep_config.name, peep_config.attribs, peep_config.gender)
    peep.ld = garbler_config.starting_ld-garbler_config.ld_spend

    places = []

    garbler = Garbler(crumbs, thesaurus_vocabulary["thesaurus"],
                      thesaurus_vocabulary["vocabulary"], peep, garbler_config)

    for x in range(0, events_count):
        places.append(garbler.get_place())
        # put back once we have enough crumbs not to crash
        # get event of the type needed at this index by the template
        # events.append(garbler.get_event(template['events'][x]))

    ##remove later
    event = garbler.get_event(template['events'][1])

    drawerer = Drawerer(None)

    drawed = drawerer.combine(event.calculated_outcomes)

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


