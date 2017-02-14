from Garbler import Garbler
import unittest

class GarblerTests(unittest.TestCase):
    def setUp(self):
        self.garbler = Garbler("C:\\_source\\garbler\\files\\config")

    def tearDown(self):
        self.garbler = None

    def testGetCrumbsWithInspection(self):
        crumbs = self.garbler.get_crumbs(True)

    def testReturnsEvent(self):
        event = self.garbler.run_to_end_auto()
        self.assertTrue(event.text != '')
        self.assertTrue(event.text != None)
        self.assertTrue(len(event.text) > 1)