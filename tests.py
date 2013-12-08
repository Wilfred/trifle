import unittest

from lexer import lex
from parser import parse_one
from trifle_types import List, Integer, Symbol, TRUE, FALSE
from evaluator import evaluate, evaluate_with_built_ins
from errors import UnboundVariable, TrifleTypeError, LexFailed

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


class SymbolLex(unittest.TestCase):
    def test_lex_symbol(self):
        self.assertEqual(
            lex("x")[0], Symbol('x'))

        self.assertEqual(
            lex("x1")[0], Symbol('x1'))

        self.assertEqual(
            lex("foo?")[0], Symbol('foo?'))

    def test_lex_invalid_symbol(self):
        with self.assertRaises(LexFailed):
            lex("\\")


class BooleanLex(unittest.TestCase):
    def test_lex_boolean(self):
        self.assertEqual(
            lex("true")[0], TRUE)

        self.assertEqual(
            lex("false")[0], FALSE)

    def test_lex_symbol_leading_bool(self):
        """Ensure that a symbol which starts with a valid boolean literal, is
        still a valid symbol.

        """
        self.assertEqual(
            lex("true-foo")[0], Symbol('true-foo'))


class Parsing(unittest.TestCase):
    def test_parse_list(self):
        expected_parse_tree = List()
        expected_parse_tree.append(Integer(1))
        expected_parse_tree.append(Integer(2))

        self.assertEqual(parse_one(lex("(1 2)")),
                         expected_parse_tree)


class Evaluating(unittest.TestCase):
    def test_invalid_function(self):
        with self.assertRaises(TrifleTypeError):
            evaluate_with_built_ins(parse_one(lex("(1)")))


# todo: test evaluating numbers
class EvaluatingLiterals(unittest.TestCase):
    def test_eval_boolean(self):
        self.assertEqual(
            evaluate_with_built_ins(parse_one(lex("true"))),
            TRUE)

        self.assertEqual(
            evaluate_with_built_ins(parse_one(lex("false"))),
            FALSE)


class Quote(unittest.TestCase):
    def test_eval_boolean(self):
        expected = parse_one(lex("(+ 1 2)"))
        
        self.assertEqual(
            evaluate_with_built_ins(parse_one(lex("(quote (+ 1 2))"))),
            expected)


class Addition(unittest.TestCase):
    def test_addition(self):
        self.assertEqual(evaluate_with_built_ins(parse_one(lex("(+)"))),
                         Integer(0))
        
        self.assertEqual(evaluate_with_built_ins(parse_one(lex("(+ 1)"))),
                         Integer(1))
        
        self.assertEqual(evaluate_with_built_ins(parse_one(lex("(+ 1 2)"))),
                         Integer(3))

    def test_invalid_type(self):
        with self.assertRaises(TrifleTypeError):
            evaluate_with_built_ins(parse_one(lex("(+ +)")))


class Subtraction(unittest.TestCase):
    def test_subtraction(self):
        self.assertEqual(evaluate_with_built_ins(parse_one(lex("(-)"))),
                         Integer(0))
        
        self.assertEqual(evaluate_with_built_ins(parse_one(lex("(- 1)"))),
                         Integer(-1))
        
        self.assertEqual(evaluate_with_built_ins(parse_one(lex("(- 5 2)"))),
                         Integer(3))

    def test_invalid_type(self):
        with self.assertRaises(TrifleTypeError):
            evaluate_with_built_ins(parse_one(lex("(- -)")))


class Same(unittest.TestCase):
    def test_booleans_same(self):
        self.assertEqual(
            evaluate_with_built_ins(parse_one(lex("(same? true true)"))),
            TRUE)

        self.assertEqual(
            evaluate_with_built_ins(parse_one(lex("(same? false false)"))),
            TRUE)

    def test_booleans_different(self):
        self.assertEqual(
            evaluate_with_built_ins(parse_one(lex("(same? true false)"))),
            FALSE)

    def test_integers_same(self):
        self.assertEqual(
            evaluate_with_built_ins(parse_one(lex("(same? 1 1)"))),
            TRUE)

    def test_integers_different(self):
        self.assertEqual(
            evaluate_with_built_ins(parse_one(lex("(same? 1 2)"))),
            FALSE)

    def test_different_types(self):
        self.assertEqual(
            evaluate_with_built_ins(parse_one(lex("(same? true 1)"))),
            FALSE)


class Environment(unittest.TestCase):
    def test_evaluate_variable(self):
        env = {
            'x': Integer(1),
        }
        self.assertEqual(evaluate(parse_one(lex("x")), env),
                         Integer(1))

    def test_unbound_variable(self):
        with self.assertRaises(UnboundVariable):
            evaluate_with_built_ins(parse_one(lex("x")))

        
if __name__ == '__main__':
    unittest.main()
