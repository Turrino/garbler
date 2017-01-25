from utils import Utils

class Peep:
    def __init__(self, name, attributes, gender):
        self.name = name
        self.desc = ""
        self.gender = gender
        self.attributes = attributes
        self.ld = 0
        self.items = []
        # to do: attributes

class Outcome:
    def __init__(self, text, connotation, canvas_id):
        self.text = text
        self.connotation = connotation
        self.drops = []
        self.canvas_id = canvas_id
        self.ld_sparkle = False  # when the outcome was altered by the use of ld, use this indicator

class Canvas:
    def __init__(self, identifier, background, overlay, static=None):
        self.id = identifier
        self.background = background
        self.overlay = overlay
        self.static = static

# Modifiers stem from characters, items and possibly other things too. Some mods are unique to each category,
# while some are common and may stack (e.g. an item increasing a mod that a character already has).
class Modifier():
    def __init__(self, id, multipliers):
        self.id = id  # this matches the id of an attribute
        #  this is a list of integers lists (each inner list being a list of two;
        #  the event to be influenced, and the strength of the effect
        self.multipliers = multipliers

class Item:
    def __init__(self, type, attributes, durability, name):
        self.type = type
        self.attributes = attributes
        self.durability = durability
        self.name = name

    def print_attributes(self):
        description = ""
        for attr in self.attributes:
            description += " {0} attr: {1}".format(attr.id, attr.level)
        return description



class Crumbs:
    def __init__(self, instructions, thesaurus, vocabulary, blocks, story_fundamentals,
                 drops, mods, attributes, entry_point_type):
        self.instructions = instructions
        self.thesaurus = thesaurus
        self.vocabulary = vocabulary
        self.blocks = blocks
        self.fundamentals = story_fundamentals
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