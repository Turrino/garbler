from builders.ForkParser import ForkParser
import unittest

class ReplParserTests(unittest.TestCase):
    def setUp(self):
        block = { 'name': 'name', 'branches': { '1': {}, '2': {}, '3': {}, '4': {}} }
        self.fp = ForkParser(block)

    def testReadPointer(self):
        expected_pointer = '1'
        res = self.fp.parse_pointer(f'to {expected_pointer}')
        self.assertEquals(expected_pointer, res[0])

    def testReadSwitch(self):
        expect_target = 'x'
        expect_text1 = 'a b c'
        expect_text2 = 'c d e'
        expect_token1 = '-'
        expect_token2 = '+'
        expect_pointer1 = '1'
        expect_pointer2 = '2'
        expect_pointer3 = '3'
        expect_pointer4 = '4'

        test_string = f'switch {expect_target}:' \
                      f' {{{expect_text1}}}:' \
                      f' {expect_token1} to {expect_pointer1};' \
                      f' {expect_token2} to {expect_pointer2};' \
                      f' {{{expect_text2}}}:' \
                      f' {expect_token1} to {expect_pointer3};' \
                      f' {expect_token2} to {expect_pointer4};'

        ts2 = 'switch owner: {Accept the task.}: + to 1; - to 2; {Refuse.}: + to 3; - to 4;'

        res = self.fp.parse_switch_choice(test_string)

        self.assertEquals(expect_target, res.target)
        self.assertEquals(expect_text1, res.choices[0].text)
        self.assertEquals(expect_token1, res.choices[0].pointers[0].token)
        self.assertEquals(expect_pointer1, res.choices[0].pointers[0].pointer)
        self.assertEquals(expect_token2, res.choices[0].pointers[1].token)
        self.assertEquals(expect_pointer2, res.choices[0].pointers[1].pointer)
        self.assertEquals(expect_token1, res.choices[1].pointers[0].token)
        self.assertEquals(expect_pointer3, res.choices[1].pointers[0].pointer)
        self.assertEquals(expect_token2, res.choices[1].pointers[1].token)
        self.assertEquals(expect_pointer4, res.choices[1].pointers[1].pointer)