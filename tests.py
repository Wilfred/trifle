import unittest

from lexer import lex
from parser import Node, Leaf, parse, parse_one
from baobab_types import Integer
from evaluator import evaluate

"""Baobab unit tests. These are intended to be run with CPython, and
no effort has been made to make them RPython friendly.

"""

class IntegerLex(unittest.TestCase):
    def test_lex_number(self):
        self.assertEqual(
            lex("123")[0], Integer(123))


class Parsing(unittest.TestCase):
    def test_parse_list(self):
        expected_parse_tree = Node()
        expected_parse_tree.append(Leaf(Integer(1)))
        expected_parse_tree.append(Leaf(Integer(2)))

        self.assertEqual(parse_one(lex("(1 2)")),
                         expected_parse_tree)


class Evaluating(unittest.TestCase):
    def test_eval_addition(self):
        self.assertEqual(evaluate(parse_one(lex("(+)"))),
                         Integer(0))
        
        self.assertEqual(evaluate(parse_one(lex("(+ 1)"))),
                         Integer(1))
        
        self.assertEqual(evaluate(parse_one(lex("(+ 1 2)"))),
                         Integer(3))
        
if __name__ == '__main__':
    unittest.main()
