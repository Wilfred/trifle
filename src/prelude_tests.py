import unittest

from trifle_types import List, Integer, TRUE, FALSE
from main import env_with_prelude
from evaluator import evaluate
from parser import parse_one
from lexer import lex


"""Unit tests for functions and macros in the prelude. It's easier to
test in Python than in Trifle, since Trifle code uses many parts of
the prelude very often.

"""

class ListTest(unittest.TestCase):
    def test_list(self):
        expected = List()
        expected.values = [Integer(1), Integer(2), Integer(3)]

        self.assertEqual(
            evaluate(parse_one(lex("(list 1 2 3)")),
                     env_with_prelude()),
            expected)


class MapTest(unittest.TestCase):
    def test_map(self):
        expected = List()
        expected.values = [Integer(2), Integer(3), Integer(4)]

        self.assertEqual(
            evaluate(parse_one(lex("(map (lambda (x) (+ x 1)) (list 1 2 3))")),
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


class NotTest(unittest.TestCase):
    def test_not_booleans(self):
        self.assertEqual(
            evaluate(parse_one(lex("(not true)")),
                     env_with_prelude()),
            FALSE)
        
        self.assertEqual(
            evaluate(parse_one(lex("(not false)")),
                     env_with_prelude()),
            TRUE)

    def test_not_truthiness(self):
        self.assertEqual(
            evaluate(parse_one(lex("(not (list))")),
                     env_with_prelude()),
            TRUE)
        
        self.assertEqual(
            evaluate(parse_one(lex("(not 123)")),
                     env_with_prelude()),
            FALSE)
