import unittest

from trifle_types import List, Integer
from main import env_with_prelude
from evaluator import evaluate
from parser import parse_one
from lexer import lex


"""Unit tests for functions and macros in the prelude.

"""

# todo: write a unit test library in trifle so we don't need to write
# our tests in Python.

class ListTest(unittest.TestCase):
    def test_list(self):
        expected = List()
        expected.values = [Integer(1), Integer(2), Integer(3)]

        self.assertEqual(
            evaluate(parse_one(lex("(list 1 2 3)")),
                     env_with_prelude()),
            expected)

class NthItemTest(unittest.TestCase):
    def test_first(self):
        self.assertEqual(
            evaluate(parse_one(lex("(first (list 1 2 3 4 5))")),
                     env_with_prelude()),
            Integer(1))
        
    def test_second(self):
        self.assertEqual(
            evaluate(parse_one(lex("(second (list 1 2 3 4 5))")),
                     env_with_prelude()),
            Integer(2))
        
    def test_third(self):
        self.assertEqual(
            evaluate(parse_one(lex("(third (list 1 2 3 4 5))")),
                     env_with_prelude()),
            Integer(3))
        
    def test_fourth(self):
        self.assertEqual(
            evaluate(parse_one(lex("(fourth (list 1 2 3 4 5))")),
                     env_with_prelude()),
            Integer(4))
        
    def test_fifth(self):
        self.assertEqual(
            evaluate(parse_one(lex("(fifth (list 1 2 3 4 5))")),
                     env_with_prelude()),
            Integer(5))
