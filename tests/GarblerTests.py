import unittest
import wrgrbrler
from builders.Garbler import Garbler


class ModParserTests(unittest.TestCase):
    def setUp(self):
        self.grblr = wrgrbrler.get_default_garbler()

    def tearDown(self):
        self.grblr = None

    def testStuffTheBlanks(self):
        test_text = 'bla @£speshul£type_a#1,1@ and @sample_instructions@ @creature$0@ @character@ and @item#1@ and this one '
        filled_in = self.grblr.stuff_the_blanks(test_text)
        self.assertEqual({None}, filled_in)#todo
