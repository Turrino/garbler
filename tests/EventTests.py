from Garbler import Garbler
import os
import unittest

class EventTests(unittest.TestCase):
    def setUp(self):
        grblr = Garbler(os.path.join(os.path.dirname(__file__), "..", "files\\config"))
        self.event = grblr.event
        demo_type = "demo"
        self.event.chosinator = TestChosinator()
        self.expected = "carrot"
        self.not_expected = "stick"
        self.expected_loc = "crowbar"
        self.event.entry_point_type = demo_type
        grblr.crumbs.vocabulary[self.expected_loc] = self.expected
        grblr.crumbs.blocks[demo_type] = [{'args': [],
                                    'type': demo_type,
                                    'name': demo_type,
                                    'branches':  {1: {'situation': '',
                                                      'choice': [{'to': 2, 'level': 0, 'text': ''},
                                                                 {'to': 3, 'level': 0, 'text': ''}]},
                                                  2: {'situation': self.not_expected}, 3: {'situation': self.expected}},
                                    'location_types': [self.expected_loc]}]
        self.event.run_to_end()


    def testPicksTheCorrectChoicePath(self):
        self.assertTrue(self.event.text.find(self.expected) > -1)
        self.assertFalse(self.event.text.find(self.expected) == -1)

    def testPicksTheCorrectLocation(self):
        self.assertEqual(self.event.tracker[0]["location"].text, self.expected)
        self.assertEqual(self.event.tracker[0]["location"].subtype, self.expected_loc)

class TestChosinator:
    @staticmethod
    def choose(options):
        return 3
