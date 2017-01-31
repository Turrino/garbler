from builders.Event import Event
import wrgrbrler
import unittest

class EventTests(unittest.TestCase):
    def setUp(self):
        garbler = wrgrbrler.get_default_garbler()
        crumbs = wrgrbrler.get_crumbs()
        self.event = Event(crumbs, garbler, AutoChosinator)
        demo_type = "demo"
        self.expected = "carrot"
        self.not_expected = "stick"
        self.event.entry_point_type = demo_type
        crumbs.blocks[demo_type] = [{'args': [],
                                    'type': demo_type,
                                    'name': demo_type,
                                    'branches':  {1: {'situation': '',
                                                      'choice': [{'to': 2, 'level': 0, 'text': ''},
                                                                 {'to': 3, 'level': 0, 'text': ''}]},
                                                  2: {'situation': self.not_expected}, 3: {'situation': self.expected}},
                                    'canvas_id': -1}]

    def tearDown(self):
        self.attributes = None

    def testPicksTheCorrectChoicePath(self):
        self.event.run_to_end()
        self.assertTrue(self.event.text.find(self.expected) > -1)
        self.assertFalse(self.event.text.find(self.expected) == -1)

class AutoChosinator:
    @staticmethod
    def choose(options):
        return 3