from Garbler import Garbler
import unittest

class GarblerTests(unittest.TestCase):
    def setUp(self):
        self.garbler = Garbler("C:\\_source\\garbler\\files\\config", True)

    def tearDown(self):
        self.garbler = None

    def testGetCrumbsWithInspection(self):
        crumbs = self.garbler.get_crumbs(True)

    def testReturnsEvent(self):
        event = self.garbler.run_to_end_auto()
        self.assertTrue(event.text != '')
        self.assertTrue(event.text != None)
        self.assertTrue(len(event.text) > 1)

    def testAddsRootContext(self):
        self.garbler.add_context("{this: yalla, and: the, that: best}")
        self.assertEquals("yalla", self.garbler.crumbs.story_cache["this"])
        self.assertEquals("the", self.garbler.crumbs.story_cache["and"])
        self.assertEquals("best", self.garbler.crumbs.story_cache["that"])

    def testAddsKeyedContext(self):
        self.garbler.add_context("{identifier: yalla the best, blarg: blorg}")
        self.assertEquals({"identifier": "yalla the best", "blarg": "blorg"},
                          self.garbler.crumbs.story_cache["yalla the best"])

    def testParsesSimpleAddedContext(self):
        self.garbler.add_context("{instructions: $creature}")
        #todo fix this, it's borken
        self.assertEquals({"instructions": "idk?"},
                          self.garbler.crumbs.story_cache["instructions"])

    def testParsesNestedAddedContext(self):
        #todo ditto
        self.garbler.add_context("{instructions: { part1: $creature, part2: [ $type_a, $type_b ]}}")
        self.assertEquals({"instructions": "idk?"},
                          self.garbler.crumbs.story_cache["instructions"])



