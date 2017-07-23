from pyparsing import *

valid_parameters = 't'
element = Word(printables, excludeChars='-')
parameters = Suppress('-') + Word(valid_parameters).setResultsName('parameter_name')
entry = Group(element.setResultsName('text') + Optional(OneOrMore(parameters)).setResultsName('params'))
grammar = OneOrMore(entry).setResultsName('entries')


def parse_instructions(text):
    return grammar.parseString(text)