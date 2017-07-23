from models.Models import Meta
from models.Inflection import *

def get_pluralisation(amount):
    if amount < 1:
        raise ValueError('Amount cannot be less than 1')
    return False if amount == 1 else True

class Entity(Meta):
    def __init__(self, element, elem_id, gender, overlay_pos=None, amount=1):
        if gender not in [0,1]:
            raise ValueError('Subset for an entity (gender) can only be 0 (f) or 1 (m)')
        super().__init__(element, elem_id, overlay_pos, gender)
        self.pluralisation = get_pluralisation(amount)
