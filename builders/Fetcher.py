import random
import math
from Crumbs import *


class Fetcher:
    def __init__(self, parsed_crumbs):
        self.crumbs = parsed_crumbs

    #use get_meta to return both the string and the metadata
    def writerer(self, crumblists, subset=None, get_meta=False):
        fetch_crumb = Utils.any_of_many
        # We use this only if a subset parameter (mood, gender...) is passed in, in order to access the sub-features
        # Then check if the selected element is a list - some elements are universal and do not have a subset
        def fetch_subset(words):
            pick = Utils.any_of_many(words)
            return pick[subset] if type(pick) is list else pick

        if subset is not None:
            fetch_crumb = fetch_subset

        wroted = ""
        meta = []

        for item in crumblists:
            #todo this happens when there are not enough crumbs and they all get used up; reload them as a last resort?
            if not len(item.crumbs):
                element = "POTATO"
            else:
                element = fetch_crumb(item.crumbs)
            meta.append(element)
            wroted = "{0} {1}".format(wroted, element)

        if get_meta:
            return wroted[1:], meta
        else:
            return wroted[1:]

    # accepts a list of strings that indicate the crumbs path to the desired element
    # returns a tuple with: [0][0] actual text, [0][1] metadata lookup keys,
    # [1] actual path (will differ from category_path if ~ was used)
    def get_element(self, object_name, subset=-1):
        instructions = self.crumbs.find_instructions(object_name)
        self.fill_in_crumblist(instructions)
        text_info = self.writerer(instructions.crumblists, subset, True)
        return Element(instructions.sub_type, text_info[0], text_info[1])

    def fill_in_crumblist(self, instructions):
        for entry in instructions.descriptor:
            if entry not in self.crumbs.vocabulary.keys():
                # instructions may contain specific crumblists, or a super-type with multiple categories
                # if it is a super-type, then traverse it until we find something we can use
                single_item = self.crumbs.lookup_thesaurus(entry)
                if single_item is None:
                    raise ValueError("Could not find crumblist for: {0}.".format(entry))
                subtype = single_item["type"]
                item = single_item["item"]
            else:
                subtype = entry
                item = entry
            instructions.crumblists.append(Crumblist(subtype, self.crumbs.vocabulary[item]))

    def create_item(self, drop_info):
        name = self.get_element(drop_info[0])
        tier = random.randrange(1, drop_info[1]+1)

        points = tier*2
        minimum_allocation = math.floor(points/10) if points/10>1 else 1
        durability = random.randrange(minimum_allocation, points-minimum_allocation+1)
        modpoints = points - durability
        # pick modifiers that are consistent with that item type
        # make a copy of the list so that we're not removing things from the actual attributes table
        attributes_list = list(self.crumbs.item_attr[drop_info[0]])
        chosen_attributes = {}

        while modpoints > 0:
            if modpoints == 1:
                chosen_attributes[Utils.any_of_many(attributes_list)] = 1
                modpoints -= 1
            else:
                if (len(attributes_list) > 1):
                    allocation = math.floor(modpoints/2)
                else:
                    allocation = modpoints

                modpoints -= allocation
                #50% chance, half the points go into one mod, 50% chance they go into two mods
                multiple_allocation = random.randrange(0,2)
                if multiple_allocation and len(attributes_list) > 2:
                    chosen_attributes[Utils.any_of_many(attributes_list)] = allocation/2
                    chosen_attributes[Utils.any_of_many(attributes_list)] = allocation/2
                else:
                    chosen_attributes[Utils.any_of_many(attributes_list)] = allocation

        return {"type": drop_info[0], "attributes": chosen_attributes,
                 "durability": durability, "name": name}



