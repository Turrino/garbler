import random

class Utils:
    @staticmethod
    def any_of_many(elements, discard_item=True):
        randomness = random.randrange(0, len(elements))
        item = elements[randomness]
        if discard_item:
            elements.remove(item)
        return item

    @staticmethod
    def find_specific(composite_item):
        while type(composite_item) is dict:
            composite_item = composite_item[random.choice(list(composite_item.keys()))]
        if type(composite_item) is list:
            composite_item = Utils.any_of_many(composite_item, False)
        return composite_item
