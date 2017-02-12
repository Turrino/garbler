from Garbler import Garbler
import unittest

class GarblerTests(unittest.TestCase):
    def setUp(self):
        self.grblr = Garbler("C:\\_source\\garbler\\files\\config")

    def tearDown(self):
        self.grblr = None

    def testGetCrumbsWithInspection(self):
        crumbs = self.grblr.get_crumbs(True)

    def testReturnsEvent(self):
        event = self.grblr.run_to_end()
        self.assertTrue(event.text != '')
        self.assertTrue(event.text != None)
        self.assertTrue(len(event.text) > 1)