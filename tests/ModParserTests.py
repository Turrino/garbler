import unittest
from builders.ModParser import ModParser


class ModParserTests(unittest.TestCase):
    def setUp(self):
        self.item_type = "a"
        self.attributes = {
            "Items": {"a": [], "b": []},
            "Character": ["x", "y"]
            }
        self.fundamentals = {"context":
                             {"peep":
                              {"items": [{"type": self.item_type, "attributes": [],
                                          "durability": 0, "name": "name"},
                                         {"type": self.item_type, "attributes": [],
                                          "durability": 0, "name": "name2"}],
                               "attributes": {"x": 3}}}}


    def tearDown(self):
        self.attributes = None

    def testGetRndMod(self):
        mod = ModParser.parse("random 33".split(" "), self.attributes)
        self.assertEqual({"percentage": "33"}, mod.args)
        self.assertEqual("rnd", mod.method)

    def testApplyRndMod(self):
        mod = ModParser.parse("random 100".split(" "), self.attributes)
        result = mod.apply(self.fundamentals)
        self.assertTrue(result)

    def testGetHasMod(self):
        mod = ModParser.parse("has a 12".split(" "), self.attributes)
        self.assertEqual({"item_type": "a", "amount": "12"}, mod.args)
        self.assertEqual("has_item", mod.method)

    def testApplyHasModSingleQuantity(self):
        mod = ModParser.parse("has a".split(" "), self.attributes)
        result = mod.apply(self.fundamentals)
        self.assertTrue(result)

    def testApplyHasModMultipleQuantity(self):
        mod = ModParser.parse("has a 2".split(" "), self.attributes)
        result = mod.apply(self.fundamentals)
        self.assertTrue(result)

    def testApplyHasModFails(self):
        mod = ModParser.parse("has a 3".split(" "), self.attributes)
        result = mod.apply(self.fundamentals)
        self.assertFalse(result)

    def testGetIsMod(self):
        mod = ModParser.parse("is x >= 3".split(" "), self.attributes)
        self.assertEqual({"attribute": "x", "comparison": ">=", "against": "3"}, mod.args)
        self.assertEqual("has_attribute", mod.method)

    def testApplyIsModSuccessBiggerThan(self):
        mod = ModParser.parse("is x > 2".split(" "), self.attributes)
        result = mod.apply(self.fundamentals)
        self.assertTrue(result)

    def testApplyIsModSuccessBiggerOrEqualThan(self):
        mod = ModParser.parse("is x >= 3".split(" "), self.attributes)
        result = mod.apply(self.fundamentals)
        self.assertTrue(result)

    def testApplyIsModSuccessSmallerThan(self):
        mod = ModParser.parse("is x < 4".split(" "), self.attributes)
        result = mod.apply(self.fundamentals)
        self.assertTrue(result)

    def testApplyIsModSuccessSmallerOrEqualThan(self):
        mod = ModParser.parse("is x <= 3".split(" "), self.attributes)
        result = mod.apply(self.fundamentals)
        self.assertTrue(result)

    def testApplyIsModFailsBiggerThan(self):
        mod = ModParser.parse("is x > 3".split(" "), self.attributes)
        result = mod.apply(self.fundamentals)
        self.assertFalse(result)

    def testApplyIsModFailsSmallerThan(self):
        mod = ModParser.parse("is x < 3".split(" "), self.attributes)
        result = mod.apply(self.fundamentals)
        self.assertFalse(result)

    def testApplyIsModFailsBiggerEqualThan(self):
        mod = ModParser.parse("is x >= 4".split(" "), self.attributes)
        result = mod.apply(self.fundamentals)
        self.assertFalse(result)

    def testApplyIsModFailsSmallerEqualThan(self):
        mod = ModParser.parse("is x =< 2".split(" "), self.attributes)
        result = mod.apply(self.fundamentals)
        self.assertFalse(result)
