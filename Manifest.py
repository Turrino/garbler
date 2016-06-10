class Manifest:
    def __init__(self):
        self.peeps = []
        self.places = []

class Peep:
    def __init__(self, name, gender):
        self.name = name
        self.gender = gender
        #to do: attributes

class Place:
    def __init__(self, name):
        self.name = name
        #to do: uh, something to define the place better if we need to (if not, remove this class)

class Event:
    def __init__(self, event_args):
        self.type = event_args["type"]
        self.place = event_args["place"]
        #to do: self.place = event_args["mood"]
        self.friends = event_args["friends"]
        self.foes = event_args["foes"]
        self.items = event_args["items"]