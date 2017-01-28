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

            if replacement[0] == '%':
                stored_info = story_cache[replacement[1:]]
                repl_as_text = ' '.join(stored_info["keys"])
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

                overlay_pos = []
                display_data = True if replacement.find('#') > -1 else False
                if display_data:  # trim+save the overlay data and leave the clean replacement
                    splat = replacement.split('#')
                    if len(splat) != 1 and splat.count('') != len(splat)-1:
                        overlay_pos = (splat[1]).split(',') if replacement.find(',') else splat[1]
                        overlay_pos = [int(x) for x in overlay_pos]
                    replacement = splat[0]

                parsed_repl = get_element(replacement, subset)
                repl_as_text = parsed_repl[0]
                meta = {"keys": parsed_repl[1], "display": display_data,
                        "type": replacement, "position": overlay_pos,
                        "cache_id": repl_id, "subset": subset}
                metadata.append(meta)
                if must_remember:
                    story_cache[repl_id] = meta

            replacements.append(repl_as_text)

        filled_in_text = ""

        trail = parameters_text[-1:][0] if len(parameters_text) % 2 != 0 else ""

        for i in range(0, len(parameters_text) - 1, 2):
            filled_in_text += parameters_text[i] + replacements[int(i / 2)]

        return filled_in_text + trail, metadata