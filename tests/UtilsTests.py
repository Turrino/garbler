import unittest
from Garbler import Garbler
from builders.Fetcher import Fetcher
from builders.Utils import Utils


class UtilsTest(unittest.TestCase):
    def setUp(self):
        self.fetcher = Fetcher(Garbler("C:\\_source\\garbler\\files\\config").crumbs)
        self.default_text = 'this should not get deleted by a '
        self.cache = {}
        self.repl_type = 'type_a'
        self.cache_id = 'speshul'
        def parse(x): return Utils.stuff_the_blanks(x, self.cache, self.fetcher.get_element)
        self.parse_txt = parse

    def tearDown(self):
        self.fetcher = None

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
        self.assertFalse(parsed_item.display)
        self.assertTrue(type(parsed_item.element.meta) is list)
        self.assertTrue(type(parsed_item.element.text) is str)
        self.assertEqual(parsed_item.element.subtype, repl_type)
        self.assertEqual(parsed_item.cache_id, None)

    def testVisibility(self):
        test_text = '{0} @creature#1,1@'.format(self.default_text)
        filled_in = self.parse_txt(test_text)
        self.assertTrue(self.default_text in filled_in[0])
        parsed_item = filled_in[1][0]
        self.assertTrue(parsed_item.display)
        self.assertEqual([1,1], parsed_item.position)

    def testSubset(self):
        test_text = '{0} @creature$1@'.format(self.default_text)
        filled_in = self.parse_txt(test_text)
        self.assertTrue(self.default_text in filled_in[0])
        parsed_item = filled_in[1][0]
        self.assertEqual(1, parsed_item.subset)

    def setupCache(self):
        test_text = '{0} @£{1}£{2}@'.format(self.default_text, self.cache_id, self.repl_type)
        return self.parse_txt(test_text)

    def testCachesReplacements(self):
        filled_in = self.setupCache()
        self.assertTrue(self.default_text in filled_in[0])
        parsed_item = filled_in[1][0]
        self.assertTrue(type(parsed_item.element.meta) is list)
        self.assertEqual(parsed_item.element.subtype, self.repl_type)
        self.assertEqual(parsed_item.cache_id, self.cache_id)

    def testCachedReplacements(self):
        filled_in = self.setupCache()
        test_text = '{0} @%{1}@'.format(self.default_text, self.cache_id)
        self.assertTrue(self.default_text in filled_in[0])
        self.assertTrue(self.cache[self.cache_id].element.text in filled_in[0])
