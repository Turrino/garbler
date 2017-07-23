from pyparsing import *

class ForkParser:
    def __init__(self, block):
        self.block = block
        self.wrapper = None

        # Common definitions
        words = Combine(OneOrMore(Word(printables, excludeChars='{}') | White(' ')))
        # todo make this token list configurable (more than two tokens)
        token = Word('+-', max=1).setResultsName('token')
        pointer_id = Word(printables, excludeChars=':;').setParseAction(self.validate_pointer).setResultsName('pointer')
        simple_pointer = Group('to' + pointer_id)
        tokenized_pointer = Group(token + 'to' + pointer_id)
        pointers = delimitedList(tokenized_pointer, delim=";")
        # switches
        choice = Group('{' + Combine(OneOrMore(words)).setResultsName('text') + '}:' + pointers.setResultsName('pointers'))
        # complete forms
        self.simple_pointer_grammar = simple_pointer
        self.switch_grammar = ("switch" + Word(printables, excludeChars=':;').setResultsName('target') + ':' \
                              + delimitedList(choice, delim=';').setResultsName('choices'))


    def validate_pointer(self, pointer_id):
        if pointer_id[0] not in self.block["branches"].keys():
            raise ValueError(f'Pointer "{pointer_id}" does not point to any branch ({self.block["name"]})')

    def update_block(self):
        for key, item in self.block["branches"].items():
            if "fork" in item.keys():
                item["fork"] = self.parse(item["fork"])

        return self.block

    def parse(self, text):
        if (text[:6] == "switch"):
            return self.parse_switch_choice(text)
        else:
            return self.parse_pointer(text)

    def parse_switch_choice(self, text):
        result = self.switch_grammar.parseString(text)
        return result

    def parse_pointer(self, text):
        result = self.simple_pointer_grammar.parseString(text)
        pointer_id = result[0].pointer

        return pointer_id
