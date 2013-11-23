import unittest

from lexer import lex
from parser import Node, Leaf, parse
from baobab_types import Integer

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

        simple_list = Node()
        simple_list.append(Leaf(Integer("1")))
        simple_list.append(Leaf(Integer("2")))

        expected_parse_tree.append(simple_list)

        self.assertEqual(parse(lex("(1 2)")), expected_parse_tree)

if __name__ == '__main__':
    unittest.main()
