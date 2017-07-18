import random
from models.Models import *

repl_token = '@'
cache_token = '#'

class Utils:
    @staticmethod
    def any_of_many(elements, discard_item=True):
        if type(elements) is not list:
            return elements
        randomness = random.choice(elements)
        item = elements[randomness]
        if discard_item:
            elements.remove(item)
        return item

    @staticmethod
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


    @staticmethod
    def find_specific(composite_item, original_type):
        sub_type = original_type
        sub_item = composite_item
        while (type(sub_item) is not str):
            while type(sub_item) is dict:
                sub_type = random.choice(list(sub_item.keys()))
                sub_item = sub_item[sub_type]
            while type(sub_item) is list:
                sub_item = Utils.any_of_many(sub_item, False)
        return {"item": sub_item, "type": sub_type}

    @staticmethod
    def transform_all(instructions, transform, filter):
        for key, value in instructions.items():
            if isinstance(value, str) and filter(value):
                instructions[key] = transform(value)
            if isinstance(value, list):
                instructions[key] = [transform(x) if filter(x) else x for x in value]
            if isinstance(value, dict):
                instructions[key] = Utils.transform_all(value, transform, filter)
        return instructions

    @staticmethod
    def get_individual_replacement(text, story_cache, get_element):
        #todo use pyparsing for this
        if text[0] in ['%', '!']:
            text = text[1:]
            check_for_display_data = Utils.check_for_display_data(text)
            text = check_for_display_data.replacement
            overlay_pos = check_for_display_data.display

            cached_elem = story_cache[text]
            if isinstance(cached_elem, Meta):
                stored_info = story_cache[text].copy()
                #parsed_repl = stored_info["object"].text
                stored_info.display = True if len(overlay_pos) else False
                stored_info.position = overlay_pos
            else:
                stored_info = cached_elem
            return stored_info
        else:
            # mark the elements that we have to cache
            must_remember = text[0] == '£'
            repl_id = None
            if must_remember:
                id_and_repl = text.split('£')
                id_and_repl.remove("")
                repl_id = id_and_repl[0]
                text = id_and_repl[1]

            subset = text.find('$')
            if subset > -1:
                splat = text.split('$')
                text = splat[0] + splat[1][1:]  # take the $ tag and subset out, put the rest back
                subset = int(splat[1][:1])

            check_for_display_data = Utils.check_for_display_data(text)
            text = check_for_display_data.replacement
            overlay_pos = check_for_display_data.display

            parsed_repl = get_element(text, subset)
            meta = Meta(parsed_repl, repl_id, overlay_pos, subset)
            #metadata.append(meta)
            if must_remember:
                story_cache[repl_id] = meta
            return meta

    @staticmethod
    def create_replacements(parameters_text, story_cache, get_element):
        positions = [pos for pos, char in enumerate(parameters_text) if char == repl_token]

        if len(positions) == 0:
            return parameters_text, []

        if len(positions) % 2 != 0:
            raise ValueError("tags are not even in text: {0}".format(parameters_text))

        subs = []
        for i in range(0, len(positions), 2):
            # create a list of (replacement type, [repl startpos, repl endpos])
            subs.append((parameters_text[positions[i]:positions[i + 1] + 1], [positions[i], positions[i + 1] + 1]))

        metadata = []
        replacements = []
        parameters_text = parameters_text.split(sp_token)

        for sub in subs:
            replacement = sub[0][1:-1]

            parsed = Utils.get_individual_replacement(replacement, story_cache, get_element)
            metadata.append(parsed)
            replacements.append(parsed.element.text if isinstance(parsed, Meta) else parsed)

        filled_in_text = ""

        trail = parameters_text[-1:][0] if len(parameters_text) % 2 != 0 else ""

        for i in range(0, len(parameters_text) - 1, 2):
            filled_in_text += parameters_text[i] + replacements[int(i / 2)]

        #todo change to a proper retun type. do we need the meta to be passed around like this?
        return filled_in_text + trail, metadata

    #todo review and update the # symbol - already used by the cache
    # @staticmethod
    # def check_for_display_data(replacement):
    #     overlay_pos = []
    #     display_data = True if replacement.find('#') > -1 else False
    #     if display_data:  # trim+save the overlay data and leave the clean replacement
    #         splat = replacement.split('#')
    #         if len(splat) != 1 and splat.count('') != len(splat) - 1:
    #             overlay_pos = (splat[1]).split(',') if replacement.find(',') else splat[1]
    #             overlay_pos = [int(x) for x in overlay_pos]
    #         replacement = splat[0]
    #     return DisplayData(overlay_pos, replacement)
