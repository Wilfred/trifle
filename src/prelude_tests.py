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
