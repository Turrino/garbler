from models.Models import Instructions
from builders.InstructionsParser import parse_instructions
import random

def any_of_many(elements, discard_item=True):
    if type(elements) is not list:
        return elements
    randomness = random.choice(elements)
    item = elements[randomness]
    if discard_item:
        elements.remove(item)
    return item

def read_crumb_package(content, instructions):
    for k, v in content['crumbs'].items():
        parsed = parse_instructions(v)
        type_indicator = next(next(entry for prm in entry.params if prm == 't')
                              for entry in parsed.entries if len(entry.params))
        instructions[k] = Instructions(content['type'], k, type_indicator[0], v)

def create_cached_element(instruction, crumbs, cache_key, primer_reference, fetcher):
    def cache_element(instr_to_fetch, qualified_name):
        # todo allow lists in here? maybe
        element = fetcher.get_element(instr_to_fetch)
        crumbs.story_cache[qualified_name] = element

    def unpack_instructions(primer_dict, base_name):
        for k, v in primer_dict.items():
            if isinstance(v, str):
                cache_element(v, base_name + "." + k)
            else:
                unpack_instructions(v, base_name + "." + k)

    # check if it is a complex (dict) instruction that needs unpacking
    if isinstance(instruction, dict):
        # todo: this is to make sure we don't unpack them multiple times;
        # find a better way so that we don't have useless stuff in the dictionary
        # crumbs.story_cache[primer_reference] = None
        unpack_instructions(instruction, cache_key)
    else:
        cache_element(instruction, cache_key)


def find_specific(composite_item, original_type):
    sub_type = original_type
    sub_item = composite_item
    while (type(sub_item) is not str):
        while type(sub_item) is dict:
            sub_type = random.choice(list(sub_item.keys()))
            sub_item = sub_item[sub_type]
        while type(sub_item) is list:
            sub_item = any_of_many(sub_item, False)
    return {"item": sub_item, "type": sub_type}


def transform_all(instructions, transform, filter):
    for key, value in instructions.items():
        if isinstance(value, str) and filter(value):
            instructions[key] = transform(value)
        if isinstance(value, list):
            instructions[key] = [transform(x) if filter(x) else x for x in value]
        if isinstance(value, dict):
            instructions[key] = transform_all(value, transform, filter)
    return instructions
