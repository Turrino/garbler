from builders.Utils import Utils

class Canvas:
    def __init__(self, identifier, background, overlay, static=None):
        self.id = identifier
        self.background = background
        self.overlay = overlay
        self.static = static

class Crumbs:
    def __init__(self, instructions, thesaurus, vocabulary, blocks, story_fundamentals,
                 drops, mods, attributes, entry_point_type):
        self.instructions = instructions
        self.thesaurus = thesaurus
        self.vocabulary = vocabulary
        self.blocks = blocks
        self.fundamentals = story_fundamentals
        self.main_char = self.fundamentals["context"]["peep"]
        self.drops = drops
        self.mods = mods
        self.item_attr = attributes["Items"]
        self.char_attr = attributes["Character"]
        self.entry_point_type = entry_point_type
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

    def lookup_thesaurus(self, crumblist_name):
        return self.find_instructions(crumblist_name, True)

    # finds a crumblist using the map (returns [0]: crumblist, [1]: crumbs path)
    def find_instructions(self, crumblist_name, lookup_thesaurus = False):
        target_map = self.instructions_map if not lookup_thesaurus else self.thesaurus_map
        target = self.instructions if not lookup_thesaurus else self.thesaurus

        if crumblist_name not in target_map.keys():
            return crumblist_name

        full_path = target_map[crumblist_name]

        #If it's not at the root level of the crumbs, find it
        if len(full_path) != 0:
            for path_level in full_path:
                target = target[path_level]

        instructions = target[crumblist_name]

        if type(instructions) is not str:
            return Utils.find_specific(instructions)
        else:
            return instructions