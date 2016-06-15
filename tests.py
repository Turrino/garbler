import unittest
from wrgrbrler import Wrgrbrler
import json


class Wrgrbrler_tests(unittest.TestCase):
    def setUp(self):
        self.crumbs = None
        with open('files/breadcrumbs') as crumbs_file:
            crumbs = json.load(crumbs_file)
        self.garbler = Wrgrbrler(crumbs)

    def tearDown(self):
        self.crumbs = None
        self.garbler = None

    def testGetPeepDesc(self):
        test_peep = self.garbler.get_peep("test_name").desc
        self.assertTrue(type(test_peep) is str)
        self.assertTrue(len(test_peep) > 10)
        self.assertTrue(len(test_peep) < 100)

    def testGetPlace(self):
        test_place = self.garbler.get_place().name
        self.assertTrue(type(test_place) is str)
        self.assertTrue(len(test_place) > 10)
        self.assertTrue(len(test_place) < 100)