import unittest
import Garbler
from builders.Utils import Utils


class UtilsTest(unittest.TestCase):
    def setUp(self):
        self.grblr = Garbler.get_default_garbler()
        self.default_text = 'this should not get deleted by a '

        def parse(x): return Utils.stuff_the_blanks(x, {}, self.grblr.get_element)
        self.parse_txt = parse

    def tearDown(self):
        self.grblr = None

    def testInvalidInstructions(self):
        with self.assertRaises(ValueError) as context:
            self.parse_txt('invalid text, @ tag is not closed')
        self.assertTrue(type(context.exception) is ValueError)

    def testSampleInstructions(self):
        repl_type = 'sample_instructions'
        test_text = '{0} @{1}@'.format(self.default_text, repl_type)
        filled_in = self.parse_txt(test_text)
        self.assertTrue(self.default_text in filled_in[0])
        parsed_item = filled_in[1][0]
        self.assertFalse(parsed_item["display"])
        self.assertTrue(type(parsed_item["keys"]) is list)
        self.assertEqual(parsed_item["type"], repl_type)
        self.assertEqual(parsed_item["cache_id"], None)

    def testVisibility(self):
        test_text = '{0} @creature#1,1@'.format(self.default_text)
        filled_in = self.parse_txt(test_text)
        self.assertTrue(self.default_text in filled_in[0])
        parsed_item = filled_in[1][0]
        self.assertTrue(parsed_item["display"])
        self.assertEqual([1,1], parsed_item["position"])

    def testSubset(self):
        test_text = '{0} @creature$1@'.format(self.default_text)
        filled_in = self.parse_txt(test_text)
        self.assertTrue(self.default_text in filled_in[0])
        parsed_item = filled_in[1][0]
        self.assertEqual(1, parsed_item["subset"])

    def testCachedReplacements(self):
        repl_type = 'type_a'
        cache_id = 'speshul'
        test_text = '{0} @£{1}£{2}@'.format(self.default_text, cache_id, repl_type)
        filled_in = self.parse_txt(test_text)
        self.assertTrue(self.default_text in filled_in[0])
        parsed_item = filled_in[1][0]
        self.assertTrue(type(parsed_item["keys"]) is list)
        self.assertEqual(parsed_item["type"], repl_type)
        self.assertEqual(parsed_item["cache_id"], cache_id)

