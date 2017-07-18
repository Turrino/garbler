from builders.Utils import Utils
from models.Models import *

class Crumbs:
    def __init__(self, instructions, thesaurus, vocabulary, blocks, story_fundamentals,
                 primers, drops, mods, attributes):
        self.instructions = instructions
        self.thesaurus = thesaurus
        self.vocabulary = vocabulary
        self.blocks = blocks
        self.primers = primers
        self.mods = mods

        # todo make more generic. remove items & ld from the cache defaults
        self.story_cache = {"fundamentals": story_fundamentals, "ld": 0, "items": []}
        self.drops = drops
        self.item_attr = attributes["Items"]
        self.char_attr = attributes["Character"]

        self.instructions_map = {}
        self.thesaurus_map = {}
        self.path_mapper(self.instructions_map, self.instructions)
        self.path_mapper(self.thesaurus_map, self.thesaurus)

    # populates the specified map so that crumblists, thesaurus etc
    # can be accessed without needing to know the explicit path to nested objects
    def path_mapper(self, map_to, current_level, c_path=None):
        if c_path is None:
            c_path = []

        for element in current_level:
            map_to[element] = c_path
            if type(current_level[element]) in [list, str]:
                continue
            else:
                map_to[element] = c_path
                sub_path = c_path[:]
                sub_path.append(element)
                self.path_mapper(map_to, current_level[element], sub_path)

    def find_instructions(self, lookup_name):
        if self.check_keys(lookup_name, self.instructions_map):
            full_path = self.instructions_map[lookup_name]
            target = self.instructions
            #If it's not at the root level of the crumbs, find it
            result = self.traverse_path(full_path, target)[lookup_name]

            if type(result) is not str:
                found = Utils.find_specific(result, lookup_name)
                return Instructions(found["type"], found["item"])
            else:
                return Instructions(lookup_name, result)
        else:
            return Instructions(lookup_name, lookup_name)

    def lookup_thesaurus(self, lookup_name):
        if self.check_keys(lookup_name, self.thesaurus_map):
            full_path = self.thesaurus_map[lookup_name]
            target = self.thesaurus
            result = self.traverse_path(full_path, target)

            if type(result) is not str:
                return Utils.find_specific(result, lookup_name)
            else:
                return result
        elif self.check_keys(lookup_name, self.vocabulary):
            return lookup_name

    def check_keys(self, lookup_name, target):
        if lookup_name not in target.keys():
            if type(lookup_name) is str:
                return False
            else:
                raise ValueError("Cannot lookup: {0}".format(lookup_name))
        return True

    def traverse_path(self, path, target):
        if len(path) != 0:
            for path_level in path:
                target = target[path_level]
        return target