import unittest
from lexer import lex

"""Baobab unit tests. These are intended to be run with CPython, and
no effort has been made to make them RPython friendly.

"""

class IntegerLex(unittest.TestCase):
    def test_lex_number(self):
        self.assertEqual(lex("123"), [('integer', '123')])


if __name__ == '__main__':
    unittest.main()
