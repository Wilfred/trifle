import unittest

from lexer import lex
from parser import Node, Leaf, parse_one
from trifle_types import Integer
from evaluator import evaluate
from errors import UnboundVariable

"""Trifle unit tests. These are intended to be run with CPython, and
no effort has been made to make them RPython friendly.

"""

class IntegerLex(unittest.TestCase):
    def test_lex_positive_number(self):
        self.assertEqual(
            lex("123")[0], Integer(123))

        self.assertEqual(
            lex("0123")[0], Integer(123))

    def test_lex_negative_number(self):
        self.assertEqual(
            lex("-123")[0], Integer(-123))

    def test_lex_zero(self):
        self.assertEqual(
            lex("0")[0], Integer(0))

        self.assertEqual(
            lex("-0")[0], Integer(0))


class Parsing(unittest.TestCase):
    def test_parse_list(self):
        expected_parse_tree = Node()
        expected_parse_tree.append(Leaf(Integer(1)))
        expected_parse_tree.append(Leaf(Integer(2)))

        self.assertEqual(parse_one(lex("(1 2)")),
                         expected_parse_tree)


class Evaluating(unittest.TestCase):
    def test_eval_addition(self):
        self.assertEqual(evaluate(parse_one(lex("(+)")), {}),
                         Integer(0))
        
        self.assertEqual(evaluate(parse_one(lex("(+ 1)")), {}),
                         Integer(1))
        
        self.assertEqual(evaluate(parse_one(lex("(+ 1 2)")), {}),
                         Integer(3))


class Environment(unittest.TestCase):
    def test_evaluate_variable(self):
        env = {
            'x': Integer(1),
        }
        self.assertEqual(evaluate(parse_one(lex("x")), env),
                         Integer(1))

    def test_unbound_variable(self):
        with self.assertRaises(UnboundVariable):
            evaluate(parse_one(lex("x")), {})

        
if __name__ == '__main__':
    unittest.main()
