class Manifest:
    def __init__(self, peep, places, events):
        self.peep = peep
        self.places = places
        self.events = events

class Peep:
    def __init__(self, name, attributes, gender):
        self.name = name
        self.desc = ""
        self.gender = gender
        self.attributes = attributes
        self.ld = 0
        self.items = []
        #to do: attributes

class Place:
    def __init__(self, name):
        self.name = name
        #to do: uh, something to define the place better if we need to (if not, remove this class)

class Outcome:
    def __init__(self, text, connotation):
        self.text = text
        self.connotation = connotation
        self.drops = []

#Modifiers stem from characters, items and possibly other things too. Some mods are unique to each category,
#while some are common and may stack (e.g. an item increasing a mod that a character already has).
class Modifier():
    def __init__(self, id, multipliers):
        self.id = id #this matches the id of an attribute
        #  this is a list of integers lists (each inner list being a list of two;
        #  the event to be influenced, and the strength of the effect
        self.multipliers = multipliers

class Attribute():
    def __init__(self, id, level):
        self.id = id
        self.level = level

class Filter:
    def __init__(self, character_modifiers, item_modifiers, luck_modifier):
        self.char_mod = character_modifiers
        self.item_mod = item_modifiers
        self.luck_mod = luck_modifier

class Pointer:
    def __init__(self, to_id, text):
        self.to_id = to_id
        self.text = text

class Segment:
    def __init__(self, outcomes, filtr):
        self.outcomes = outcomes
        self.filtr = filtr

class SegmentBlock:
    def __init__(self, id, segments, fork):
        self.id = id
        self.segments = segments
        self.fork = fork

class Event:
    def __init__(self, event_args, blocks):
        self.type = event_args['type']
        self.mood = event_args['mood']
        self.blocks = blocks
        self.text = ""

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

class Config:
    def __init__(self, starting_ld, ld_spend, ld_variance):
        self.starting_ld = starting_ld
        self.ld_spend = ld_spend
        self.ld_variance = ld_variance

        # to do:
        #self.place = event_args["place"]
        #self.place = event_args["mood"]
        #self.friends = event_args["friends"]
        #self.foes = event_args["foes"]
        #self.items = event_args["items"]