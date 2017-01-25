import unittest
from builders.ModParser import ModParser


class ModParserTests(unittest.TestCase):
    def setUp(self):
        self.attributes = {
            "Items": {"a": [], "b": []},
            "Character": ["x", "y"]
            }

    def tearDown(self):
        self.attributes = None

    def testGetRndMod(self):
        mod = ModParser.parse("random 33", self.attributes)
        self.assertEqual({"percentage": 33}, mod.args)
        self.assertEqual(ModParser.rnd, mod.process)

    def testGetHasMod(self):
        mod = ModParser.parse("has a 12", self.attributes)
        self.assertEqual({"item_type": "a", "amount": 12}, mod.args)
        self.assertEqual(ModParser.has_item, mod.process)

    def testGetIsMod(self):
        mod = ModParser.parse("is x >= 3", self.attributes)
        self.assertEqual({"attribute": "x", "comparison": ">=", "value": 3}, mod.args)
        self.assertEqual(ModParser.has_attribute, mod.process)