import unittest
import yaml
from builders.CrumbUtils import read_crumb_package
from builders.InstructionsParser import parse_instructions


example = 'pickles pie-t'
instructions = '{ type: "!!python/name:models.Story.Entity", crumbs: {test: ' + example + ' } }'


class InstructionsParserTests(unittest.TestCase):
    def testParseInstructions(self):
        res = parse_instructions(example)
        self.assertEqual(2, len(res.entries))
        self.assertEqual('t', res.entries[1].params[0])

    def testGetsCorrectTypeParameter(self):
        res = {}
        read_crumb_package(yaml.load(instructions), res)
        self.assertEqual(1, len(res))
        self.assertEqual('pie', res['test'].type_indicator)
