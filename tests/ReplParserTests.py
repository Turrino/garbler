import unittest
from builders.ReplParser import ReplParser


class ReplParserTests(unittest.TestCase):
    def testForkParse(self):
        expected = "chicken"
        tag = "@a@"

        def action(x):
            return expected

        cases = ["{0}", "x{0}", "{0}x", "{0}x{0}", "x{0}x{0}x", "{0}x{0}x", "x{0}x{0}", "x{0}{0}x",
                 "{0}{0}", "{0} {0}", " {0}{0}", "{0}{0} ", " {0} {0} "]

        for item in cases:
            test1 = ReplParser.split(item.format(tag), "@", action)
            self.assertEqual(item.format(expected), test1)