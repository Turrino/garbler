from Garbler import Garbler
import os
import unittest
from models.Models import Choice

class EventTests(unittest.TestCase):
    def setUp(self):
        grblr = Garbler(os.path.join(os.path.dirname(__file__), "..", "files\\config"))
        self.event = grblr.event
        self.crumbs = grblr.crumbs
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
        self.text_a = "a"
        self.text_b = "b"
        self.text_c = "c"
        self.event.entry_point_type = demo_type
        grblr.crumbs.vocabulary[self.expected_loc] = self.expected
        grblr.crumbs.blocks[demo_type] = [{'args': [],
                                    'type': demo_type,
                                    'name': demo_type,
                                    'out_args': [ self.out_arg, self.out_arg2, self.out_arg3 ],
                                    'primers': { self.out_arg2: self.primer2 },
                                    'branches':  {'1': {'situation': self.text_a,
                                                        'fork': [{'to': '2', 'if': None, 'text': ''}]},
                                                  '2': {'situation': self.text_b,
                                                        'choice': [{'to': '3', 'level': '0', 'text': ''},
                                                                   {'to': 'x', 'level': '0', 'text': ''}]},
                                                  '3': {'situation': self.text_c,
                                                        'choice': [{'to': '5', 'level': '0', 'text': ''},
                                                                   {'to': 'x', 'level': '0', 'text': ''}]},
                                                  '4': {'situation': self.not_expected},
                                                  '5': {'situation': self.expected}},
                                    'location_types': [self.expected_loc]}]

    def consumeEvent(self):
        choice = None
        while not self.event.complete:
            fork = self.event.step(choice)
            if type(fork) is Choice:
                choice = TestChosinator.choose(fork)

    def testGetsCorrectTextBatches(self):
        text_batches = []
        choice = None
        while not self.event.complete:
            fork = self.event.step(choice)
            if type(fork) is Choice:
                text_batches.append(self.event.get_text_batch())
                choice = TestChosinator.choose(fork)
        text_batches.append(self.event.get_text_batch())
        #Branch 1 is a fork, so that will be bunched up with #2
        #Branches 3 (choice) and 5 (terminal) should be individual batches, 4 should not be in
        self.assertEquals("{0} {1}".format(self.text_a, self.text_b), text_batches[0])
        self.assertEquals(self.text_c, text_batches[1])
        self.assertEquals(self.expected, text_batches[2])
        self.assertEquals(3, len(text_batches))

    def testPicksTheCorrectChoicePath(self):
        self.consumeEvent()
        self.assertTrue(self.event.text.find(self.expected) > -1)
        self.assertFalse(self.event.text.find(self.expected) == -1)

    def testPicksTheCorrectLocation(self):
        self.consumeEvent()
        self.assertEqual(self.event.tracker[0]["location"].text, self.expected)
        self.assertEqual(self.event.tracker[0]["location"].subtype, self.expected_loc)

    def testLoadsTheCorrectPrimers(self):
        self.consumeEvent()
        self.assertEqual(self.simple_repl, self.crumbs.story_cache[self.out_arg].text)
        self.assertEqual(self.simple_repl2, self.crumbs.story_cache[self.out_arg2].text)

    def testLoadsNestedPrimersCorrectly(self):
        self.consumeEvent()
        full_qualifier = self.out_arg3 + "." + self.outer_qualifier + "." + self.inner_qualifier
        self.assertTrue(full_qualifier in self.crumbs.story_cache.keys())
        self.assertEqual(self.simple_repl, self.crumbs.story_cache[self.out_arg].text)

class TestChosinator:
    @staticmethod
    def choose(fork):
        return fork.options[0].to