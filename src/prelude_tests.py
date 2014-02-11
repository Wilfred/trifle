import unittest

from trifle_types import List, Integer, TRUE, FALSE, NULL
from main import env_with_prelude
from evaluator import evaluate, evaluate_all
from trifle_parser import parse_one, parse
from lexer import lex


"""Unit tests for functions and macros in the prelude. It's easier to
test in Python than in Trifle, since Trifle code uses many parts of
the prelude very often.

"""

class SetTest(unittest.TestCase):
    def test_set(self):
        self.assertEqual(
            evaluate_all(
                parse(lex(u"(set! x 1) x")), env_with_prelude()),
            Integer(1))

    def test_set_returns_null(self):
        self.assertEqual(
            evaluate(
                parse_one(lex(u"(set! x 1)")), env_with_prelude()),
            NULL)


class DoTest(unittest.TestCase):
    def test_do(self):
        self.assertEqual(
            evaluate(parse_one(lex(u"(do 1 2)")), env_with_prelude()),
            Integer(2))

    def test_do_no_args(self):
        self.assertEqual(
            evaluate(parse_one(lex(u"(do)")), env_with_prelude()),
            NULL)


class IncTest(unittest.TestCase):
    def test_inc(self):
        self.assertEqual(
            evaluate(parse_one(lex(u"(inc 5)")), env_with_prelude()),
            Integer(6))

    def test_inc_macro(self):
        self.assertEqual(
            evaluate_all(parse(lex(u"(set! x 2) (inc! x) x")), env_with_prelude()),
            Integer(3))


class DecTest(unittest.TestCase):
    def test_dec(self):
        self.assertEqual(
            evaluate(parse_one(lex(u"(dec 5)")), env_with_prelude()),
            Integer(4))

    def test_dec_macro(self):
        self.assertEqual(
            evaluate_all(parse(lex(u"(set! x 2) (dec! x) x")), env_with_prelude()),
            Integer(1))


class ForEachTest(unittest.TestCase):
    def test_for_each(self):
        self.assertEqual(
            evaluate(parse_one(lex(u"""(let (total 0 numbers (list 1 2 3 4))
            (for-each number numbers (set! total (+ total number)))
            total)""")), env_with_prelude()),
            Integer(10))


class ListTest(unittest.TestCase):
    def test_list(self):
        expected = List([Integer(1), Integer(2), Integer(3)])

        self.assertEqual(
            evaluate(parse_one(lex(u"(list 1 2 3)")),
                     env_with_prelude()),
            expected)


class MapTest(unittest.TestCase):
    def test_map(self):
        expected = List([Integer(2), Integer(3), Integer(4)])

        self.assertEqual(
            evaluate(parse_one(lex(u"(map (lambda (x) (+ x 1)) (list 1 2 3))")),
                     env_with_prelude()),
            expected)


class NthItemTest(unittest.TestCase):
    def test_first(self):
        self.assertEqual(
            evaluate(parse_one(lex(u"(first (list 1 2 3 4 5))")),
                     env_with_prelude()),
            Integer(1))
        
    def test_second(self):
        self.assertEqual(
            evaluate(parse_one(lex(u"(second (list 1 2 3 4 5))")),
                     env_with_prelude()),
            Integer(2))
        
    def test_third(self):
        self.assertEqual(
            evaluate(parse_one(lex(u"(third (list 1 2 3 4 5))")),
                     env_with_prelude()),
            Integer(3))
        
    def test_fourth(self):
        self.assertEqual(
            evaluate(parse_one(lex(u"(fourth (list 1 2 3 4 5))")),
                     env_with_prelude()),
            Integer(4))
        
    def test_fifth(self):
        self.assertEqual(
            evaluate(parse_one(lex(u"(fifth (list 1 2 3 4 5))")),
                     env_with_prelude()),
            Integer(5))


class LastTest(unittest.TestCase):
    def test_last(self):
        self.assertEqual(
            evaluate(parse_one(lex(u"(last (list 1 2 3 4 5))")),
                     env_with_prelude()),
            Integer(5))


class NotTest(unittest.TestCase):
    def test_not_booleans(self):
        self.assertEqual(
            evaluate(parse_one(lex(u"(not true)")),
                     env_with_prelude()),
            FALSE)
        
        self.assertEqual(
            evaluate(parse_one(lex(u"(not false)")),
                     env_with_prelude()),
            TRUE)

    def test_not_truthiness(self):
        self.assertEqual(
            evaluate(parse_one(lex(u"(not (list))")),
                     env_with_prelude()),
            TRUE)
        
        self.assertEqual(
            evaluate(parse_one(lex(u"(not 123)")),
                     env_with_prelude()),
            FALSE)
