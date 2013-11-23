import unittest

from lexer import lex
from baobab_types import Integer

"""Baobab unit tests. These are intended to be run with CPython, and
no effort has been made to make them RPython friendly.

"""

class IntegerLex(unittest.TestCase):
    def test_lex_number(self):
        self.assertEqual(
            lex("123")[0], Integer(123))


if __name__ == '__main__':
    unittest.main()
