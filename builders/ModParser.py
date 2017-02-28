import random


class ModParser:
    @staticmethod
    def parse_all(mods, attribute_dict):
        parsed = {}
        for key, value in mods.items():
            parsed[key] = ModParser.parse(value.split(" "), attribute_dict)
        return parsed

    @staticmethod
    def parse(splat, attributes):
        if splat[0] == "random":
            if len(splat) != 2:
                raise ValueError('descriptive error here')
            # try casting, but pass as string - it will be cast to string anyway if serialised to JSON
            int(splat[1])
            mod = Mod({"percentage": splat[1]}, "rnd")

        elif splat[0] == "has":
            #todo allow parsing target parameters who and inventory
            if splat[1] not in attributes["Items"].keys():
                raise ValueError('descriptive error here')
            amount = splat[2] if len(splat) == 3 else 1
            int(amount)
            args = {"item_type": splat[1], "amount": amount}
            mod = Mod(args, "has_item")

        elif splat[0] == "is":
            # todo allow parsing target parameters who and attributes
            if splat[1] not in attributes["Character"] or len(splat) != 4:
                raise ValueError('descriptive error here')
            int(splat[3])
            args = {"attribute": splat[1], "comparison": splat[2], "against": splat[3]}
            mod = Mod(args, "has_attribute")

        else:
            raise ValueError('descriptive error here')

        return mod


class Mod:
    def __init__(self, args, method):
        self.args = args
        self.method = method

    def apply(self, story_cache):
        self.args["story_cache"] = story_cache
        return getattr(Methods, self.method)(**self.args)

class Methods:
    @staticmethod
    def rnd(percentage, **kwargs):
        return random.randrange(0, 100) < int(percentage)

    @staticmethod
    def has_item(story_cache, item_type, amount=1, who="main", inventory="items"):
        counter = int(amount)
        for item in story_cache[who][inventory]:
            if item["type"] == item_type:
                if counter == 1:
                    return True
                else:
                    counter -= 1
        return False

    @staticmethod
    def has_attribute(story_cache, attribute, comparison, against, who="main", attributes="attributes"):
        against = int(against)
        has_attr = attribute in story_cache[who][attributes]
        amount = story_cache[who][attributes][attribute] if has_attr else 0
        if amount == against and comparison.find('=') != -1:
            return True
        if amount > against and comparison.find('>') != -1:
            return True
        if amount < against and comparison.find('<') != -1:
            return True
        return False
