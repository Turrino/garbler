from pyparsing import *

def split_repl(text, token, repl_handler):
    expr = QuotedString(token).setParseAction(repl_handler)
    return expr.transformString(text)

def resolve_repl(text, story_cache, get_element):
    # First pass: all non-cached replacements
    repl_token = "@"
    first_pass = split_repl(text, repl_token, handle_replacement)
    # Second pass: cached replacements
    cache_token = "#"
    second_pass = split_repl(first_pass, cache_token, cache_handler_provider(story_cache))
    return second_pass

#todo
def handle_replacement(instruction):
    return 'placeholder'

def cache_handler_provider(story_cache):
    def handler(instruction):
        return story_cache[instruction]

