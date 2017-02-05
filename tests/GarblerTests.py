from Garbler import Garbler
import unittest

class GarblerTests(unittest.TestCase):
    def setUp(self):
        self.grblr = Garbler("C:\\_source\\garbler\\garbler\\files\\config")

    def tearDown(self):
        self.grblr = None

    def testReturnsEvent(self):
        event = self.grblr.run_to_end()
        self.assertTrue(event.text != '')
        self.assertTrue(event.text != None)
        self.assertTrue(len(event.text) > 1)