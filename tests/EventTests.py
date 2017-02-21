from Garbler import Garbler
import os
import unittest
from models.Models import Choice

class EventTests(unittest.TestCase):
    def setUp(self):
        grblr = Garbler(os.path.join(os.path.dirname(__file__), "..", "files\\config"))
        self.event = grblr.event
        demo_type = "demo"
        self.event.chosinator = TestChosinator()
        self.expected = "carrot"
        self.not_expected = "stick"
        self.expected_loc = "crowbar"

        self.out_arg = "outarg"
        self.simple_instruction = "instr"
        self.simple_voc = "voc"
        self.simple_repl = "repl"

        self.out_arg2 = "outarg2"
        self.primer2 = "primer2"
        self.simple_instruction2 = "instr2"
        self.simple_voc2 = "voc2"
        self.simple_repl2 = "repl2"

        self.out_arg3 = "outarg3"
        self.outer_qualifier = "outer"
        self.inner_qualifier = "inner"
        self.complex_arg = { self.outer_qualifier: { self.inner_qualifier: self.simple_instruction } }

        grblr.crumbs.instructions[self.simple_instruction] = self.simple_voc
        grblr.crumbs.instructions_map[self.simple_instruction] = []
        # the fetcher will pop entries from this replacement as they get used up, need multiple entries
        grblr.crumbs.vocabulary[self.simple_voc] = [self.simple_repl for i in range(20)]
        grblr.crumbs.instructions[self.simple_instruction2] = self.simple_voc2
        grblr.crumbs.instructions_map[self.simple_instruction2] = []
        grblr.crumbs.vocabulary[self.simple_voc2] = [self.simple_repl2]
        # first out arg has a generic primer (not explicitly requested by the demo_type block)
        # second out arg has both generic and specific primers (specific primer is requested explicitly by the demo_type block)
        grblr.crumbs.primers[self.out_arg] = {self.out_arg : self.simple_instruction }
        grblr.crumbs.primers[self.out_arg2] = {self.out_arg2 : self.simple_instruction,
                                                self.primer2: self.simple_instruction2 }
        #out_arg3 does not have multiple primers, but one primer with nested instructions
        grblr.crumbs.primers[self.out_arg3] = {self.out_arg3: self.complex_arg}

        self.event.entry_point_type = demo_type
        grblr.crumbs.vocabulary[self.expected_loc] = self.expected
        grblr.crumbs.blocks[demo_type] = [{'args': [],
                                    'type': demo_type,
                                    'name': demo_type,
                                    'out_args': [ self.out_arg, self.out_arg2, self.out_arg3 ],
                                    'primers': { self.out_arg2: self.primer2 },
                                    'branches':  {'1': {'situation': '',
                                                      'choice': [{'to': '2', 'level': '0', 'text': ''},
                                                                 {'to': '3', 'level': '0', 'text': ''}]},
                                                  '2': {'situation': self.not_expected}, '3': {'situation': self.expected}},
                                    'location_types': [self.expected_loc]}]

        choice = None
        while not self.event.complete:
            fork = self.event.step(choice)
            if type(fork) is Choice:
                choice = TestChosinator.choose(fork)




    def testPicksTheCorrectChoicePath(self):
        self.assertTrue(self.event.text.find(self.expected) > -1)
        self.assertFalse(self.event.text.find(self.expected) == -1)

    def testPicksTheCorrectLocation(self):
        self.assertEqual(self.event.tracker[0]["location"].text, self.expected)
        self.assertEqual(self.event.tracker[0]["location"].subtype, self.expected_loc)

    def testLoadsTheCorrectPrimers(self):
        self.assertEqual(self.simple_repl, self.event.story_cache[self.out_arg].text)
        self.assertEqual(self.simple_repl2, self.event.story_cache[self.out_arg2].text)

    def testLoadsNestedPrimersCorrectly(self):
        full_qualifier = self.out_arg3 + "." + self.outer_qualifier + "." + self.inner_qualifier
        self.assertTrue(full_qualifier in self.event.story_cache.keys())
        self.assertEqual(self.simple_repl, self.event.story_cache[self.out_arg].text)

class TestChosinator:
    @staticmethod
    def choose(options):
        return "3"
