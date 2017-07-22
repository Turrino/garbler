class ReplParser:
    @staticmethod
    def resolve_replacements(text, story_cache, get_element):
        #First pass: all non-cached replacements
        repl_token = "@"
        first_pass = ReplParser.split(text, repl_token, None)
        #Second pass: cached replacements
        cache_token = "#"
        second_pass = ReplParser.split(text, cache_token, None)

        return second_pass


    @staticmethod
    def split(text, token, repl_handler):
        split = []
        replacement = False
        accumulator = 0

        def append(position, adjustment=0):
            segment = text[position - accumulator:position+adjustment]
            split.append(repl_handler(segment) if replacement else segment)

        for pos, char, last in ReplParser.lookahead(text):
            if char == token:
                if accumulator > 0:
                    append(pos)
                    accumulator = 0
                replacement = not replacement
            elif last:
                append(pos, 1)
            else:
                accumulator += 1

        return "".join(split)

    @staticmethod
    def lookahead(enumerable):
        enum = enumerate(enumerable)
        last = next(enum)
        for i, item in enum:
            yield last[0], last[1], False
            last = (i, item)
        yield last[0], last[1], True
