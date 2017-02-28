import random
from models.Models import *

class Utils:
    @staticmethod
    def any_of_many(elements, discard_item=True):
        if type(elements) is not list:
            return elements
        randomness = random.randrange(0, len(elements))
        item = elements[randomness]
        if discard_item:
            elements.remove(item)
        return item

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
    def stuff_the_blanks(parameters_text, story_cache, get_element):
        positions = [pos for pos, char in enumerate(parameters_text) if char == '@']

        if len(positions) == 0:
            return parameters_text, []

        if len(positions) % 2 != 0:
            raise ValueError("tags (@) are not even in text: {0}".format(parameters_text))

        subs = []
        for i in range(0, len(positions), 2):
            # create a list of (replacement type, [repl startpos, repl endpos])
            subs.append((parameters_text[positions[i]:positions[i + 1] + 1], [positions[i], positions[i + 1] + 1]))

        metadata = []
        replacements = []
        parameters_text = parameters_text.split('@')

        for sub in subs:
            replacement = sub[0][1:-1]

            if replacement[0] in ['%', '!']:
                replacement = replacement[1:]
                check_for_display_data = Utils.check_for_display_data(replacement)
                replacement = check_for_display_data.replacement
                overlay_pos = check_for_display_data.display

                stored_info = story_cache[replacement].copy()
                parsed_repl = stored_info["object"].text
                stored_info["display"] = True if len(overlay_pos) else False
                stored_info["position"] = overlay_pos
                metadata.append(stored_info)
            else:
                # mark the elements that we have to cache
                must_remember = replacement[0] == '£'
                repl_id = None
                if must_remember:
                    id_and_repl = replacement.split('£')
                    id_and_repl.remove("")
                    repl_id = id_and_repl[0]
                    replacement = id_and_repl[1]

                subset = replacement.find('$')
                if subset > -1:
                    splat = replacement.split('$')
                    replacement = splat[0] + splat[1][1:]  # take the $ tag and subset out, put the rest back
                    subset = int(splat[1][:1])

                check_for_display_data = Utils.check_for_display_data(replacement)
                replacement = check_for_display_data.replacement
                overlay_pos = check_for_display_data.display

                parsed_repl = get_element(replacement, subset)
                meta = Meta(parsed_repl, repl_id, overlay_pos, subset)
                metadata.append(meta)
                if must_remember:
                    story_cache[repl_id] = meta

            replacements.append(parsed_repl.text)

        filled_in_text = ""

        trail = parameters_text[-1:][0] if len(parameters_text) % 2 != 0 else ""

        for i in range(0, len(parameters_text) - 1, 2):
            filled_in_text += parameters_text[i] + replacements[int(i / 2)]

        return filled_in_text + trail, metadata

    @staticmethod
    def check_for_display_data(replacement):
        overlay_pos = []
        display_data = True if replacement.find('#') > -1 else False
        if display_data:  # trim+save the overlay data and leave the clean replacement
            splat = replacement.split('#')
            if len(splat) != 1 and splat.count('') != len(splat) - 1:
                overlay_pos = (splat[1]).split(',') if replacement.find(',') else splat[1]
                overlay_pos = [int(x) for x in overlay_pos]
            replacement = splat[0]
        return DisplayData(overlay_pos, replacement)
