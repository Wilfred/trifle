# -*- coding: utf-8 -*-
import unittest
from cStringIO import StringIO
import sys
import os

from mock import patch, Mock

from lexer import lex
from trifle_parser import parse_one, parse
from trifle_types import (List, Integer, Float, Fraction,
                          Symbol, Keyword, String, Character,
                          Lambda,
                          TRUE, FALSE, NULL,
                          FileHandle, Bytestring)
from evaluator import evaluate, evaluate_all
from errors import (UnboundVariable, TrifleTypeError,
                    LexFailed, ParseFailed, ArityError,
                    DivideByZero, StackOverflow, FileNotFound,
                    TrifleValueError, UsingClosedFile)
from environment import Environment, Scope, fresh_environment
from main import env_with_prelude

"""Trifle unit tests. These are intended to be run with CPython, and
no effort has been made to make them RPython friendly.

"""

class BuiltInTestCase(unittest.TestCase):
    def eval(self, program):
        """Evaluate this program in a fresh environment. Returns the result of
        the last expression.

        """
        return evaluate_all(parse(lex(program)), fresh_environment())


class CommentLexTest(BuiltInTestCase):
    def test_lex_comment(self):
        self.assertEqual(
            lex(u"1 ; 2 \n 3"), [Integer(1), Integer(3)])


class IntegerLexTest(BuiltInTestCase):
    def test_lex_positive_number(self):
        self.assertEqual(
            lex(u"123")[0], Integer(123))

        self.assertEqual(
            lex(u"0123")[0], Integer(123))

    def test_lex_negative_number(self):
        self.assertEqual(
            lex(u"-123")[0], Integer(-123))

    def test_lex_number_with_underscores(self):
        self.assertEqual(
            lex(u"1_000")[0], Integer(1000))

    def test_lex_zero(self):
        self.assertEqual(
            lex(u"0")[0], Integer(0))

        self.assertEqual(
            lex(u"-0")[0], Integer(0))

    def test_lex_invalid_number(self):
        with self.assertRaises(LexFailed):
            lex(u"123abc")


class FloatLexTest(BuiltInTestCase):
    def test_lex_positive(self):
        self.assertEqual(
            lex(u"123.0")[0], Float(123.0))

    def test_lex_float_leading_zero(self):
        self.assertEqual(
            lex(u"0123.0")[0], Float(123.0))

    def test_lex_negative(self):
        self.assertEqual(
            lex(u"-123.0")[0], Float(-123.0))

    def test_lex_with_underscores(self):
        self.assertEqual(
            lex(u"1_000.000_2")[0], Float(1000.0002))
        

    def test_lex_invalid(self):
        with self.assertRaises(LexFailed):
            lex(u"123.abc")

        with self.assertRaises(LexFailed):
            lex(u"123.456abc")


class FractionLexTest(BuiltInTestCase):
    def test_lex_fraction(self):
        self.assertEqual(
            lex(u"1/3")[0], Fraction(1, 3))

    def test_lex_fraction_underscore(self):
        self.assertEqual(
            lex(u"1/3_0")[0], Fraction(1, 30))

    def test_lex_fraction_to_integer(self):
        self.assertEqual(
            lex(u"2/1")[0], Integer(2))
        self.assertEqual(
            lex(u"3/3")[0], Integer(1))

    def test_lex_fraction_zero_denominator(self):
        with self.assertRaises(DivideByZero):
            lex(u"1/0")

    def test_lex_fraction_not_simplified(self):
        self.assertEqual(
            lex(u"2/6")[0], Fraction(1, 3))

    def test_lex_invalid_fraction(self):
        with self.assertRaises(LexFailed):
            lex(u"1/3/4")


class SymbolLexTest(BuiltInTestCase):
    def test_lex_symbol(self):
        self.assertEqual(
            lex(u"x")[0], Symbol(u'x'))

        self.assertEqual(
            lex(u"x1")[0], Symbol(u'x1'))

        self.assertEqual(
            lex(u"foo?")[0], Symbol(u'foo?'))

        self.assertEqual(
            lex(u"foo!")[0], Symbol(u'foo!'))

        self.assertEqual(
            lex(u"foo_bar")[0], Symbol(u'foo_bar'))

        self.assertEqual(
            lex(u"<=")[0], Symbol(u'<='))

    def test_lex_invalid_symbol(self):
        with self.assertRaises(LexFailed):
            lex(u"\\")


class KeywordLexTest(BuiltInTestCase):
    def test_lex_keyword(self):
        self.assertEqual(
            lex(u":x")[0], Keyword(u'x'))

    def test_lex_invalid_keyword(self):
        with self.assertRaises(LexFailed):
            lex(u":123")

class StringLexTest(BuiltInTestCase):
    def test_lex_string(self):
        self.assertEqual(
            lex(u'"foo"')[0], String(list(u'foo')))

        self.assertEqual(
            lex(u'"foo\nbar"')[0], String(list(u'foo\nbar')))

    def test_lex_non_ascii_string(self):
        self.assertEqual(
            lex(u'"flambé"')[0], String(list(u'flambé')))

    def test_lex_backslash(self):
        # Backslashes should be an error if not escaped.
        with self.assertRaises(LexFailed):
            lex(u'"\\"')

        self.assertEqual(
            lex(u'"\\\\"')[0], String(list(u'\\')))

    def test_lex_newline(self):
        self.assertEqual(
            lex(u'"\n"')[0], String(list(u'\n')))

        self.assertEqual(
            lex(u'"\\n"')[0], String(list(u'\n')))

    def test_lex_escaped_quote(self):
        self.assertEqual(
            lex(u'"\\""')[0], String(list(u'"')))


class CharacterLexTest(BuiltInTestCase):
    def test_lex_character(self):
        self.assertEqual(
            lex(u"'a'")[0], Character(u'a'))

    def test_lex_non_ascii_character(self):
        self.assertEqual(
            lex(u"'é'")[0], Character(u'é'))

    def test_lex_backslash(self):
        # Backslashes should be an error if not escaped.
        with self.assertRaises(LexFailed):
            lex(u"'\\'")

        self.assertEqual(
            lex(u"'\\\\'")[0], Character(u'\\'))

    def test_lex_newline(self):
        self.assertEqual(
            lex(u"'\n'")[0], Character(u'\n'))

        self.assertEqual(
            lex(u"'\\n'")[0], Character(u'\n'))

    def test_lex_escaped_quote(self):
        self.assertEqual(
            lex(u"'\\''")[0], Character(u"'"))


class BytestringLexTest(BuiltInTestCase):
    def test_lex_bytestring(self):
        self.assertEqual(
            lex(u'#bytes("foo")')[0], Bytestring([ord(c) for c in 'foo']))

    def test_lex_multiple_bytestrings(self):
        self.assertEqual(
            lex(u'#bytes("foo") #bytes("bar")')[1],
            Bytestring([ord(c) for c in 'bar']))

    def test_lex_invalid_byte(self):
        with self.assertRaises(LexFailed):
            lex(u'#bytes("flambé")')

    def test_lex_backslash(self):
        # Backslashes should be an error if not escaped.
        with self.assertRaises(LexFailed):
            lex(u'#bytes("\\")')

        self.assertEqual(
            lex(u'#bytes("\\\\")')[0], Bytestring([ord('\\')]))

    def test_lex_escaped_byte(self):
        self.assertEqual(
            lex(u'#bytes("\\xff")')[0], Bytestring([255]))

        self.assertEqual(
            lex(u'#bytes("\\xFF")')[0], Bytestring([255]))

    def test_lex_invalid_escaped_byte(self):
        # Not hexadecimal characters:
        with self.assertRaises(LexFailed):
            lex(u'#bytes("\\xgg")')

        # Not starting with \x
        with self.assertRaises(LexFailed):
            lex(u'#bytes("\\yff")')

        # Insufficient characters:
        with self.assertRaises(LexFailed):
            lex(u'#bytes("\\xa")')
        with self.assertRaises(LexFailed):
            lex(u'#bytes("\\x")')
            
        # Insufficient characters before next escaped character:
        with self.assertRaises(LexFailed):
            lex(u'#bytes("\\xa\\xaa")')


class BooleanLexTest(BuiltInTestCase):
    def test_lex_boolean(self):
        self.assertEqual(
            lex(u"#true")[0], TRUE)

        self.assertEqual(
            lex(u"#false")[0], FALSE)

    def test_lex_symbol_leading_bool(self):
        """Ensure that a literal whose prefix is a valid boolean, is still a
        lex error.

        """
        with self.assertRaises(LexFailed):
            lex(u"#trueish")


class NullLexTest(BuiltInTestCase):
    def test_lex_boolean(self):
        self.assertEqual(
            lex(u"#null")[0], NULL)


class ParsingTest(BuiltInTestCase):
    def test_parse_list(self):
        self.assertEqual(parse_one(lex(u"(1 2)")),
                         List([Integer(1), Integer(2)]))


class EvaluatingTest(BuiltInTestCase):
    def test_invalid_function(self):
        with self.assertRaises(TrifleTypeError):
            self.eval(u"(1)")


class EvaluatingLiteralsTest(BuiltInTestCase):
    def test_eval_boolean(self):
        self.assertEqual(
            self.eval(u"#true"),
            TRUE)

        self.assertEqual(
            self.eval(u"#false"),
            FALSE)

    def test_eval_integer(self):
        self.assertEqual(
            self.eval(u"123"),
            Integer(123))

    def test_eval_float(self):
        self.assertEqual(
            self.eval(u"123.4"),
            Float(123.4))

    def test_eval_fraction(self):
        self.assertEqual(
            self.eval(u"1/4"),
            Fraction(1, 4))

    def test_eval_null(self):
        self.assertEqual(
            self.eval(u"#null"),
            NULL)

    def test_eval_keyword(self):
        self.assertEqual(
            self.eval(u":foo"),
            Keyword(u"foo"))

    def test_eval_string(self):
        self.assertEqual(
            self.eval(u'"foo"'),
            String(list(u"foo")))

    def test_eval_bytes(self):
        self.assertEqual(
            self.eval(u'#bytes("foobar")'),
            Bytestring([ord(c) for c in "foobar"]))

    def test_eval_character(self):
        self.assertEqual(
            self.eval(u"'a'"),
            Character(u"a"))


class ReprTest(BuiltInTestCase):
    def test_list_repr(self):
        list_val = List([Integer(1)])
        self.assertEqual(list_val.repr(), '(1)')

    def test_bytes_repr(self):
        bytes_val = Bytestring([ord(c) for c in "\\ souffl\xc3\xa9"])

        self.assertEqual(
            bytes_val.repr(),
            '#bytes("\\\\ souffl\\xc3\\xa9")')

    def test_string_repr(self):
        string_val = String(list(u"foo"))
        self.assertEqual(string_val.repr(), '"foo"')

        string_val = String(list(u'"'))
        self.assertEqual(string_val.repr(), '"\\""')

        string_val = String(list(u"'"))
        self.assertEqual(string_val.repr(), '"\'"')

        string_val = String(list(u"\n"))
        self.assertEqual(string_val.repr(), '"\\n"')

        string_val = String(list(u'\\'))
        self.assertEqual(string_val.repr(), '"\\\\"')

    def test_integer_repr(self):
        val = Integer(12)
        self.assertEqual(val.repr(), '12')

    def test_fraction_repr(self):
        val = Fraction(1, 12)
        self.assertEqual(val.repr(), '1/12')

    def test_float_repr(self):
        val = Float(1.2)
        self.assertEqual(val.repr(), '1.200000')

    def test_character_repr(self):
        val = Character(u'a')
        self.assertEqual(val.repr(), "'a'")

        val = Character(u'\n')
        self.assertEqual(val.repr(), "'\\n'")

        val = Character(u"'")
        self.assertEqual(val.repr(), "'\\''")

        val = Character(u'\\')
        self.assertEqual(val.repr(), "'\\\\'")

    def test_bool_repr(self):
        self.assertEqual(TRUE.repr(), "#true")
        self.assertEqual(FALSE.repr(), "#false")

    def test_null_repr(self):
        self.assertEqual(NULL.repr(), "#null")


class EvaluatingLambdaTest(BuiltInTestCase):
    def test_call_lambda(self):
        self.assertEqual(
            self.eval(u"((lambda (x) x) 1)"),
            Integer(1))

    def test_call_lambda_last_value(self):
        self.assertEqual(
            self.eval(u"((lambda () 1 2))"),
            Integer(2))

    def test_call_not_lambda(self):
        with self.assertRaises(TrifleTypeError):
            self.eval(u"(1)")

        with self.assertRaises(TrifleTypeError):
            self.eval(u"(#null)")

        with self.assertRaises(TrifleTypeError):
            self.eval(u'("a")')
    
        with self.assertRaises(TrifleTypeError):
            self.eval(u'((quote (1)))')
    
    def test_call_lambda_variable_arguments(self):
        expected = List([Integer(1), Integer(2), Integer(3), Integer(4)])
        
        self.assertEqual(
            self.eval(u"((lambda (:rest args) args) 1 2 3 4)"),
            expected)

    def test_call_lambda_too_few_arguments(self):
        with self.assertRaises(ArityError):
            self.eval(u"((lambda (x) 1))")

    def test_call_lambda_too_few_variable_arguments(self):
        with self.assertRaises(ArityError):
            self.eval(u"((lambda (x y :rest args) x))")

    def test_call_lambda_too_many_arguments(self):
        with self.assertRaises(ArityError):
            self.eval(u"((lambda () 1) 2)")

    def test_lambda_wrong_arg_number(self):
        with self.assertRaises(ArityError):
            self.eval(u"(lambda)")

    def test_lambda_params_not_list(self):
        with self.assertRaises(TrifleTypeError):
            self.eval(u"(lambda foo bar)")

    def test_lambda_params_not_symbols(self):
        with self.assertRaises(TrifleTypeError):
            self.eval(u"(lambda (1 2) bar)")

    def test_evaluate_lambda(self):
        lambda_obj = self.eval(u"(lambda (x) x)")

        self.assertTrue(isinstance(lambda_obj, Lambda),
                        "Expected a lambda object but got a %s" % lambda_obj.__class__)


    def test_lambda_scope_doesnt_leak(self):
        """Ensure that defining a variable inside a lambda is accessible
        inside the body, but doesn't leak outside.

        """
        self.assertEqual(
            self.eval(u"((lambda () (set-symbol! (quote x) 2) x))"),
            Integer(2))

        with self.assertRaises(UnboundVariable):
            self.eval(u"((lambda () (set-symbol! (quote x) 2)) x)")

    def test_closure_variables(self):
        """Ensure that we can update closure variables inside a lambda.

        """
        self.assertEqual(
            self.eval(u"(set-symbol! (quote x) 1) ((lambda () (set-symbol! (quote x) 2))) x"),
            Integer(2))

    # TODO: also test for stack overflow inside macros.
    def test_stack_overflow(self):
        with self.assertRaises(StackOverflow):
            self.eval(u"(set-symbol! (quote f) (lambda () (f))) (f)")


class FreshSymbolTest(BuiltInTestCase):
    def test_fresh_symbol(self):
        self.assertEqual(
            self.eval(u"(fresh-symbol)"),
            Symbol(u"1-unnamed"))

    def test_fresh_symbol_wrong_arg_number(self):
        with self.assertRaises(ArityError):
            self.eval(u"(fresh-symbol 1)")


class SetSymbolTest(BuiltInTestCase):
    def test_set_symbol(self):
        self.assertEqual(
            self.eval(u"(set-symbol! (quote x) (quote y)) x"),
            Symbol(u"y"))

    def test_set_symbol_wrong_arg_number(self):
        with self.assertRaises(ArityError):
            self.eval(u"(set-symbol! (quote x) 1 2)")

    def test_set_symbol_returns_null(self):
        self.assertEqual(
            self.eval(u"(set-symbol! (quote x) 1)"),
            NULL)

    def test_set_symbol_first_arg_symbol(self):
        with self.assertRaises(TrifleTypeError):
            self.eval(u"(set-symbol! 1 2)")


class LetTest(BuiltInTestCase):
    def test_let(self):
        self.assertEqual(
            self.eval(u"(let (x 1) x)"),
            Integer(1))

    def test_let_access_previous_bindings(self):
        self.assertEqual(
            self.eval(u"(let (x 1 y (+ x 1)) y)"),
            Integer(2))

    def test_let_malformed_bindings(self):
        with self.assertRaises(TrifleTypeError):
            self.eval(u"(let (1 1) #null)")

    def test_let_odd_bindings(self):
        with self.assertRaises(ArityError):
            self.eval(u"(let (x 1 y) #null)")

    def test_let_not_bindings(self):
        with self.assertRaises(TrifleTypeError):
            self.eval(u"(let #null #null)")

        with self.assertRaises(ArityError):
            self.eval(u"(let)")

    def test_let_shadowing(self):
        """Ensure that variables defined in a let shadow outer variables with
        the same name.

        """
        self.assertEqual(
            self.eval(u"(set-symbol! (quote x) 1) (let (x 2) (set-symbol! (quote x) 3)) x"),
            Integer(1))

    def test_let_variables_dont_leak(self):
        """Ensure that variables defined in a let are undefined in the global scope.
        Regression test for the first variable in the bindings.

        """
        with self.assertRaises(UnboundVariable):
            self.eval(u"(let (x 1 y 2) #null) x")

    def test_let_not_function_scope(self):
        """Ensure that variables defined with set! are still available outside
        a let.

        """
        self.assertEqual(
            self.eval(u"(let () (set-symbol! (quote x) 3)) x"),
            Integer(3))


# todo: decide whether quote should construct fresh values each time
# i.e. (function foo () (set! x (quote ())) (push! x 1) x)
# what does (do (foo) (foo)) evaluate to?
class QuoteTest(BuiltInTestCase):
    def test_quote(self):
        expected = parse_one(lex(u"(+ 1 2)"))
        
        self.assertEqual(
            self.eval(u"(quote (+ 1 2))"),
            expected)

    def test_quote_wrong_number_args(self):
        with self.assertRaises(ArityError):
            self.eval(u"(quote foo bar)")

        with self.assertRaises(ArityError):
            self.eval(u"(quote)")

    def test_unquote(self):
        self.assertEqual(
            self.eval(u"(quote (unquote (+ 1 2)))"),
            Integer(3))

    def test_unquote_nested(self):
        expected = List([Symbol(u'x'), Integer(1)])
        
        self.assertEqual(
            self.eval(u"(set-symbol! (quote x) 1) (quote (x (unquote x)))"),
            expected)

    def test_unquote_star(self):
        expected = parse_one(lex(u"(baz foo bar)"))
        
        self.assertEqual(
            self.eval(u"(set-symbol! (quote x) (quote (foo bar))) (quote (baz (unquote* x)))"),
            expected)

    def test_unquote_wrong_arg_number(self):
        with self.assertRaises(ArityError):
            self.eval(u"(set-symbol! (quote x) 1) (quote (unquote x x))")

        with self.assertRaises(ArityError):
            self.eval(u"(quote (unquote))")

    def test_unquote_star_wrong_arg_number(self):
        with self.assertRaises(ArityError):
            self.eval(u"(set-symbol! (quote x) 1) (quote (list (unquote* x x)))")

        with self.assertRaises(ArityError):
            self.eval(u"(quote (list (unquote*)))")

    def test_unquote_star_top_level(self):
        with self.assertRaises(TrifleValueError):
            self.eval(u"(quote (unquote* #null))")

    def test_unquote_star_after_unquote(self):
        expected = parse_one(lex(u"(if #true (do 1 2))"))
        
        self.assertEqual(
            self.eval(
                u"(set-symbol! (quote x) #true) (set-symbol! (quote y) (quote (1 2)))"
                u"(quote (if (unquote x) (do (unquote* y))))"),
            expected)
        

class AddTest(BuiltInTestCase):
    def test_add_integers(self):
        self.assertEqual(self.eval(u"(+)"),
                         Integer(0))
        
        self.assertEqual(self.eval(u"(+ 1)"),
                         Integer(1))
        
        self.assertEqual(self.eval(u"(+ 1 2)"),
                         Integer(3))

    def test_add_floats(self):
        self.assertEqual(self.eval(u"(+ 1.0 2.0)"),
                         Float(3.0))

        # Mixing floats with other things:
        self.assertEqual(self.eval(u"(+ 1 2.0)"),
                         Float(3.0))
        self.assertEqual(self.eval(u"(+ 1/2 2.0)"),
                         Float(2.5))

    def test_add_fractions(self):
        self.assertEqual(self.eval(u"(+ 1/3 1/2)"),
                         Fraction(5, 6))
        
        self.assertEqual(self.eval(u"(+ 1 1/2)"),
                         Fraction(3, 2))
        
        self.assertEqual(self.eval(u"(+ 3/2 1/2)"),
                         Integer(2))
        
    def test_invalid_type(self):
        with self.assertRaises(TrifleTypeError):
            self.eval(u"(+ +)")


class SubtractTest(BuiltInTestCase):
    def test_subtract(self):
        self.assertEqual(self.eval(u"(-)"),
                         Integer(0))
        
        self.assertEqual(self.eval(u"(- 1)"),
                         Integer(-1))
        
        self.assertEqual(self.eval(u"(- 5 2)"),
                         Integer(3))

    def test_subtract_floats(self):
        self.assertEqual(self.eval(u"(- 1.0)"),
                         Float(-1.0))
        
        self.assertEqual(self.eval(u"(- 1.0 2.0)"),
                         Float(-1.0))
        
        self.assertEqual(self.eval(u"(- 1 2.0)"),
                         Float(-1.0))
        
        self.assertEqual(self.eval(u"(- 0.0 1)"),
                         Float(-1.0))
        
        self.assertEqual(self.eval(u"(- 0.0 1/2)"),
                         Float(-0.5))
        
    def test_subtract_fractions(self):
        self.assertEqual(self.eval(u"(- 1/2)"),
                         Fraction(-1, 2))

        self.assertEqual(self.eval(u"(- 1/2 1/4)"),
                         Fraction(1, 4))

        self.assertEqual(self.eval(u"(- 3/2 1/2)"),
                         Integer(1))

    def test_invalid_type(self):
        with self.assertRaises(TrifleTypeError):
            self.eval(u"(- -)")


class MultiplyTest(BuiltInTestCase):
    def test_multiply(self):
        self.assertEqual(self.eval(u"(*)"),
                         Integer(1))
        
        self.assertEqual(self.eval(u"(* 2)"),
                         Integer(2))
        
        self.assertEqual(self.eval(u"(* 2 3)"),
                         Integer(6))

    def test_multiply_floats(self):
        self.assertEqual(self.eval(u"(* 2.0 3.0)"),
                         Float(6.0))
        
        self.assertEqual(self.eval(u"(* 2 3.0)"),
                         Float(6.0))

        self.assertEqual(self.eval(u"(* 1/2 1.0)"),
                         Float(0.5))

    def test_multiply_fractions(self):
        self.assertEqual(self.eval(u"(* 1/2 3/5)"),
                         Fraction(3, 10))
        
        self.assertEqual(self.eval(u"(* 1/3 2)"),
                         Fraction(2, 3))
        
        self.assertEqual(self.eval(u"(* 2 1/2)"),
                         Integer(1))

    def test_invalid_type(self):
        with self.assertRaises(TrifleTypeError):
            self.eval(u"(* 1 #null)")


class DivideTest(BuiltInTestCase):
    def test_divide(self):
        self.assertEqual(self.eval(u"(/ 1 2)"),
                         Fraction(1, 2))

        self.assertEqual(self.eval(u"(/ 1 2 2)"),
                         Fraction(1, 4))

    def test_divide_floats(self):
        self.assertEqual(self.eval(u"(/ 1.0 2)"),
                         Float(0.5))
        
        self.assertEqual(self.eval(u"(/ 1.0 1/2)"),
                         Float(2.0))
        
    def test_divide_fractions(self):
        self.assertEqual(self.eval(u"(/ 1/2 1/3)"),
                         Fraction(3, 2))
        
        self.assertEqual(self.eval(u"(/ 1/2 1/2)"),
                         Integer(1))
        
    def test_divide_by_zero(self):
        with self.assertRaises(DivideByZero):
            self.eval(u"(/ 1 0)")

        with self.assertRaises(DivideByZero):
            self.eval(u"(/ 1.0 0.0)")

    def test_invalid_type(self):
        with self.assertRaises(TrifleTypeError):
            self.eval(u"(/ 1 #null)")

    def test_arity_error(self):
        with self.assertRaises(ArityError):
            self.eval(u"(/ 1)")


class ModTest(BuiltInTestCase):
    def test_mod(self):
        self.assertEqual(self.eval(u"(mod 11 10)"),
                         Integer(1))

    def test_mod_by_zero(self):
        with self.assertRaises(DivideByZero):
            self.eval(u"(mod 1 0)")

    def test_invalid_type(self):
        with self.assertRaises(TrifleTypeError):
            self.eval(u"(mod 1 #null)")

        with self.assertRaises(TrifleTypeError):
            self.eval(u"(mod 1 0.5)")

    def test_arity_error(self):
        with self.assertRaises(ArityError):
            self.eval(u"(mod 1)")

        with self.assertRaises(ArityError):
            self.eval(u"(mod 1 2 3)")


class DivTest(BuiltInTestCase):
    def test_div(self):
        self.assertEqual(self.eval(u"(div 5 2)"),
                         Integer(2))

        self.assertEqual(self.eval(u"(div -5 2)"),
                         Integer(-3))

    def test_div_by_zero(self):
        with self.assertRaises(DivideByZero):
            self.eval(u"(div 1 0)")

    def test_invalid_type(self):
        with self.assertRaises(TrifleTypeError):
            self.eval(u"(div 1 #null)")

        with self.assertRaises(TrifleTypeError):
            self.eval(u"(div 2.0 1.0)")

    def test_arity_error(self):
        with self.assertRaises(ArityError):
            self.eval(u"(div 1)")

        with self.assertRaises(ArityError):
            self.eval(u"(div 1 2 3)")


class IfTest(BuiltInTestCase):
    def test_if(self):
        self.assertEqual(
            self.eval(u"(if #true 2 3)"),
            Integer(2))

        self.assertEqual(
            self.eval(u"(if #false 4 5)"),
            Integer(5))

    def test_if_type_error(self):
        with self.assertRaises(TrifleTypeError):
            self.eval(u"(if 1 2 3)")

    def test_if_two_args_evals_condition(self):
        self.assertEqual(
            self.eval(u"(set-symbol! (quote x) #false) (if x 2 3)"),
            Integer(3))

    def test_if_wrong_number_of_args(self):
        with self.assertRaises(ArityError):
            self.eval(u"(if #true)")

        with self.assertRaises(ArityError):
            self.eval(u"(if 1 2 3 4)")


class WhileTest(BuiltInTestCase):
    def test_while_false_condition(self):
        # `(while)` is an error, but this should work as while should
        # not evaluate the body here.
        self.assertEqual(
            self.eval(u"(while #false (while))"),
            NULL)

    def test_while_true_condition(self):
        # `(while)` is an error, but this should work as while should
        # not evaluate the body here.
        self.assertEqual(
            self.eval(
                u"(set-symbol! (quote x) #true) (set-symbol! (quote y) 1)"
                u"(while x (set-symbol! (quote x) #false) (set-symbol! (quote y) 2))"
                u"y"),
            Integer(2))
        
    def test_while_wrong_number_of_args(self):
        with self.assertRaises(ArityError):
            self.eval(u"(while)")

    def test_while_type_error(self):
        with self.assertRaises(TrifleTypeError):
            self.eval(u"(while 1 (foo))")


class PrintTest(BuiltInTestCase):
    def test_print_returns_null(self):
        self.assertEqual(
            self.eval(u'(print! "foo")'),
            NULL)

    def test_print_writes_to_stdout(self):
        mock_stdout = StringIO()

        with patch('sys.stdout', mock_stdout):
            self.eval(u'(print! "foo")')

        self.assertEqual(mock_stdout.getvalue(), "foo\n")

    def test_print_handles_numbers(self):
        old_stdout = sys.stdout
        mock_stdout = StringIO()

        # Monkey-patch stdout.
        sys.stdout = mock_stdout
        
        self.eval(u'(print! 1)')

        # Undo the monkey-patch.
        sys.stdout = old_stdout

        self.assertEqual(mock_stdout.getvalue(), "1\n")

    def test_print_wrong_arg_number(self):
        with self.assertRaises(ArityError):
            self.eval(u"(print! 1 2)")


class InputTest(BuiltInTestCase):
    def test_input(self):
        mock_read = Mock()
        mock_read.return_value = "foobar\n"

        with patch('os.write'):
            with patch('os.read', mock_read):
                self.assertEqual(
                    self.eval(u'(input ">> ")'),
                    String(list(u"foobar"))
                )

    def test_input_type_error(self):
        with self.assertRaises(TrifleTypeError):
            self.eval(u"(input 1)")

    def test_input_arity_error(self):
        with self.assertRaises(ArityError):
            self.eval(u"(input)")

        with self.assertRaises(ArityError):
            self.eval(u"(input \"foo\" 1)")


class SameTest(BuiltInTestCase):
    def test_booleans_same(self):
        self.assertEqual(
            self.eval(u"(same? #true #true)"),
            TRUE)

        self.assertEqual(
            self.eval(u"(same? #false #false)"),
            TRUE)

    def test_booleans_different(self):
        self.assertEqual(
            self.eval(u"(same? #true #false)"),
            FALSE)

    def test_integers_different(self):
        self.assertEqual(
            self.eval(u"(same? 1 2)"),
            FALSE)

    def test_null_same(self):
        self.assertEqual(
            self.eval(u"(same? #null #null)"),
            TRUE)

    def test_symbol_same(self):
        self.assertEqual(
            self.eval(u"(same? (quote a) (quote a))"),
            TRUE)

    def test_list_same(self):
        self.assertEqual(
            self.eval(u"(set-symbol! (quote x) (quote ())) (same? x x)"),
            TRUE)

    def test_function_same(self):
        self.assertEqual(
            self.eval(u"(same? same? same?)"),
            TRUE)

    def test_lambda_same(self):
        self.assertEqual(
            self.eval(u"(set-symbol! (quote x) (lambda () 1)) (same? x x)"),
            TRUE)

    def test_different_types(self):
        self.assertEqual(
            self.eval(u"(same? #true 1)"),
            FALSE)

    def test_same_wrong_number_of_args(self):
        with self.assertRaises(ArityError):
            self.eval(u"(same? 1)")

        with self.assertRaises(ArityError):
            self.eval(u"(same? 1 2 3)")


class EqualTest(BuiltInTestCase):
    def test_booleans_equal(self):
        self.assertEqual(
            self.eval(u"(equal? #true #true)"),
            TRUE)

        self.assertEqual(
            self.eval(u"(equal? #false #false)"),
            TRUE)

    def test_booleans_different(self):
        self.assertEqual(
            self.eval(u"(equal? #true #false)"),
            FALSE)

    def test_integers_same(self):
        self.assertEqual(
            self.eval(u"(equal? 1 1)"),
            TRUE)

    def test_integers_different(self):
        self.assertEqual(
            self.eval(u"(equal? 1 2)"),
            FALSE)

    def test_floats_same(self):
        self.assertEqual(
            self.eval(u"(equal? 1.0 1.0)"),
            TRUE)

    def test_numbers_same(self):
        self.assertEqual(
            self.eval(u"(equal? 1.0 1)"),
            TRUE)

        self.assertEqual(
            self.eval(u"(equal? 1 1.0)"),
            TRUE)

    def test_null_equal(self):
        self.assertEqual(
            self.eval(u"(equal? #null #null)"),
            TRUE)

    def test_symbol_equal(self):
        self.assertEqual(
            self.eval(u"(equal? (quote a) (quote a))"),
            TRUE)

    def test_list_equal(self):
        # Equal
        self.assertEqual(
            self.eval(u"(equal? (quote (1 (2))) (quote (1 (2))))"),
            TRUE)

        # Same length, different values.
        self.assertEqual(
            self.eval(u"(equal? (quote (1 (2))) (quote (1 (3))))"),
            FALSE)

        # Different lengths.
        self.assertEqual(
            self.eval(u"(equal? (quote (1 (2))) (quote (1)))"),
            FALSE)

    def test_bytes_equal(self):
        self.assertEqual(
            self.eval(u'(equal? #bytes("foo") #bytes("foo"))'),
            TRUE)
        
        self.assertEqual(
            self.eval(u'(equal? #bytes("foo") #bytes("bar"))'),
            FALSE)
        
    def test_string_equal(self):
        self.assertEqual(
            self.eval(u"(equal? \"foo\" \"foo\")"),
            TRUE)

    def test_character_equal(self):
        self.assertEqual(
            self.eval(u"(equal? 'a' 'a')"),
            TRUE)

    def test_function_equal(self):
        self.assertEqual(
            self.eval(u"(equal? equal? equal?)"),
            TRUE)

    def test_lambda_equal(self):
        self.assertEqual(
            self.eval(u"(set-symbol! (quote x) (lambda () 1)) (equal? x x)"),
            TRUE)

    def test_different_types(self):
        self.assertEqual(
            self.eval(u"(equal? #true 1)"),
            FALSE)

        self.assertEqual(
            self.eval(u"(equal? (quote x) #null)"),
            FALSE)

        self.assertEqual(
            self.eval(u"(equal? 1.0 #null)"),
            FALSE)

        self.assertEqual(
            self.eval(u"(equal? 1 #null)"),
            FALSE)

        self.assertEqual(
            self.eval(u"(equal? 'a' #null)"),
            FALSE)

        self.assertEqual(
            self.eval(u'(equal? "a" #null)'),
            FALSE)

        self.assertEqual(
            self.eval(u'(equal? #bytes("a") #null)'),
            FALSE)

    def test_equal_wrong_number_of_args(self):
        with self.assertRaises(ArityError):
            self.eval(u"(equal? 1)")

        with self.assertRaises(ArityError):
            self.eval(u"(equal? 1 2 3)")


class LessThanTest(BuiltInTestCase):
    def test_less_than(self):
        self.assertEqual(
            self.eval(u"(< 1 2)"),
            TRUE)

        self.assertEqual(
            self.eval(u"(< 3 2)"),
            FALSE)

    def test_less_than_floats(self):
        self.assertEqual(
            self.eval(u"(< 1 2.0)"),
            TRUE)

        self.assertEqual(
            self.eval(u"(< 3.0 2.0)"),
            FALSE)

    def test_less_than_fractions(self):
        self.assertEqual(
            self.eval(u"(< 1 3/2)"),
            TRUE)

        self.assertEqual(
            self.eval(u"(< 1/2 1/3)"),
            FALSE)

        self.assertEqual(
            self.eval(u"(< -1/2 1/3)"),
            TRUE)

        self.assertEqual(
            self.eval(u"(< 1/2 0.1)"),
            FALSE)

    def test_less_than_typeerror(self):
        with self.assertRaises(TrifleTypeError):
            self.eval(u"(< #true #false)")

    def test_less_than_insufficient_args(self):
        with self.assertRaises(ArityError):
            self.eval(u"(<)")

        with self.assertRaises(ArityError):
            self.eval(u"(< 1)")


class LengthTest(BuiltInTestCase):
    def test_length_list(self):
        self.assertEqual(
            self.eval(u"(length (quote (2 3)))"),
            Integer(2))

    def test_length_list_string(self):
        self.assertEqual(
            self.eval(u'(length "abc")'),
            Integer(3))

    def test_length_bytestring(self):
        self.assertEqual(
            self.eval(u'(length #bytes("abc"))'),
            Integer(3))

    def test_length_typeerror(self):
        with self.assertRaises(TrifleTypeError):
            self.eval(u"(length 1)")
            
    def test_length_arg_number(self):
        with self.assertRaises(ArityError):
            self.eval(u"(length)")
            
        with self.assertRaises(ArityError):
            self.eval(u"(length (quote ()) 1)")
            

class GetIndexTest(BuiltInTestCase):
    def test_get_index_list(self):
        self.assertEqual(
            self.eval(u"(get-index (quote (2 3)) 0)"),
            Integer(2))

    def test_get_index_bytestring(self):
        self.assertEqual(
            self.eval(u'(get-index #bytes("abc") 0)'),
            Integer(97))

    def test_get_index_string(self):
        self.assertEqual(
            self.eval(u'(get-index "abc" 0)'),
            Character(u'a'))

    def test_get_index_negative_index(self):
        self.assertEqual(
            self.eval(u"(get-index (quote (2 3)) -1)"),
            Integer(3))

    def test_get_index_negative_index_error(self):
        with self.assertRaises(TrifleValueError):
            self.eval(u"(get-index (quote (2 3)) -3)")

    def test_get_index_typeerror(self):
        with self.assertRaises(TrifleTypeError):
            self.eval(u"(get-index #null 0)")

        with self.assertRaises(TrifleTypeError):
            self.eval(u"(get-index (quote (1)) #false)")

    def test_get_index_indexerror(self):
        with self.assertRaises(TrifleValueError):
            self.eval(u"(get-index (quote ()) 0)")

        with self.assertRaises(TrifleValueError):
            self.eval(u"(get-index (quote (1)) 2)")

    def test_get_index_wrong_arg_number(self):
        with self.assertRaises(ArityError):
            self.eval(u"(get-index)")

        with self.assertRaises(ArityError):
            self.eval(u"(get-index (quote (1)))")

        with self.assertRaises(ArityError):
            self.eval(u"(get-index (quote (1)) 0 0)")


class SetIndexTest(BuiltInTestCase):
    def test_set_index_list(self):
        expected = List([Integer(1)])
        
        self.assertEqual(
            self.eval(u"(set-symbol! (quote x) (quote (0))) (set-index! x 0 1) x"),
            expected)

    def test_set_index_string(self):
        expected = String(list(u"bbc"))
        
        self.assertEqual(
            self.eval(u'(set-symbol! (quote x) "abc") (set-index! x 0 \'b\') x'),
            expected)

    def test_set_index_bytestring(self):
        expected = Bytestring([ord(c) for c in "bbc"])
        
        self.assertEqual(
            self.eval(u'(set-symbol! (quote x) #bytes("abc")) (set-index! x 0 98) x'),
            expected)

    def test_set_index_bytestring_type_error(self):
        with self.assertRaises(TrifleTypeError):
            self.eval(u'(set-index! #bytes("a") 0 #null)')
        
        with self.assertRaises(TrifleTypeError):
            self.eval(u'(set-index! #bytes("a") 0 1.0)')
        
    def test_set_index_string_type_error(self):
        with self.assertRaises(TrifleTypeError):
            self.eval(u'(set-index! "abc" 0 #null)')
        
    def test_set_index_bytestring_range_error(self):
        with self.assertRaises(TrifleValueError):
            self.eval(u'(set-index! #bytes("a") 0 -1)')
        
        with self.assertRaises(TrifleValueError):
            self.eval(u'(set-index! #bytes("a") 0 256)')
        
    def test_set_index_negative(self):
        expected = List([Integer(10), Integer(1)])
        
        self.assertEqual(
            self.eval(u"(set-symbol! (quote x) (quote (10 20))) (set-index! x -1 1) x"),
            expected)

    def test_set_index_returns_null(self):
        self.assertEqual(
            self.eval(u"(set-index! (quote (2)) 0 1)"),
            NULL)

    def test_set_index_typeerror(self):
        with self.assertRaises(TrifleTypeError):
            self.eval(u"(set-index! #null 0 0)")

        with self.assertRaises(TrifleTypeError):
            self.eval(u"(set-index! (quote (1)) #false #false)")

    def test_set_index_indexerror(self):
        with self.assertRaises(TrifleValueError):
            self.eval(u"(set-index! (quote ()) 0 #true)")

        with self.assertRaises(TrifleValueError):
            self.eval(u"(set-index! (quote (1)) 2 #true)")

        with self.assertRaises(TrifleValueError):
            self.eval(u"(set-index! (quote (1 2 3)) -4 #true)")

    def test_set_index_wrong_arg_number(self):
        with self.assertRaises(ArityError):
            self.eval(u"(set-index!)")

        with self.assertRaises(ArityError):
            self.eval(u"(set-index! (quote (1)))")

        with self.assertRaises(ArityError):
            self.eval(u"(set-index! (quote (1)) 0)")

        with self.assertRaises(ArityError):
            self.eval(u"(set-index! (quote (1)) 0 5 6)")


class InsertTest(BuiltInTestCase):
    def test_insert(self):
        expected = List([Integer(1), Integer(2)])
        
        self.assertEqual(
            self.eval(u"(set-symbol! (quote x) (quote (1))) (insert! x 1 2) x"),
            expected)

    def test_insert_negative(self):
        expected = List([Integer(1), Integer(5), Integer(2)])
        
        self.assertEqual(
            self.eval(u"(set-symbol! (quote x) (quote (1 2))) (insert! x -1 5) x"),
            expected)

    def test_insert_bytestring(self):
        self.assertEqual(
            self.eval(u'(set-symbol! (quote x) #bytes("a")) (insert! x 1 98) x'),
            Bytestring([ord(c) for c in "ab"]))

    def test_insert_bytestring_invalid_type(self):
        with self.assertRaises(TrifleTypeError):
            self.eval(u'(set-symbol! (quote x) #bytes("a")) (insert! x 1 #null)')

    def test_insert_bytestring_invalid_value(self):
        with self.assertRaises(TrifleValueError):
            self.eval(u'(set-symbol! (quote x) #bytes("a")) (insert! x 1 256)')

    def test_insert_string(self):
        self.assertEqual(
            self.eval(u'(set-symbol! (quote x) "a") (insert! x 1 \'b\') x'),
            String(list(u"ab")))

    def test_insert_string_invalid_type(self):
        with self.assertRaises(TrifleTypeError):
            self.eval(u'(set-symbol! (quote x) "a") (insert! x 1 #null)')

    def test_insert_returns_null(self):
        self.assertEqual(
            self.eval(u"(insert! (quote ()) 0 1)"),
            NULL)

    def test_insert_arg_number(self):
        with self.assertRaises(ArityError):
            self.eval(u"(insert! (quote ()) 0)")

        with self.assertRaises(ArityError):
            self.eval(u"(insert! (quote ()) 0 1 2)")

    def test_insert_indexerror(self):
        with self.assertRaises(TrifleValueError):
            self.eval(u"(insert! (quote ()) 1 #null)")

        with self.assertRaises(TrifleValueError):
            self.eval(u"(insert! (quote (1 2)) -3 0)")

    def test_insert_typeerror(self):
        # first argument must be a sequence
        with self.assertRaises(TrifleTypeError):
            self.eval(u"(insert! #null 0 0)")

        # second argument must be an integer
        with self.assertRaises(TrifleTypeError):
            self.eval(u"(insert! (quote ()) 0.0 0)")


class EnvironmentVariablesTest(BuiltInTestCase):
    def test_evaluate_variable(self):
        env = Environment([Scope({
            u'x': Integer(1),
        })])
        self.assertEqual(evaluate(parse_one(lex(u"x")), env),
                         Integer(1))

    def test_unbound_variable(self):
        with self.assertRaises(UnboundVariable):
            self.eval(u"x")


class ParseTest(BuiltInTestCase):
    def test_parse(self):
        expected = parse(lex(u"(+ 1 2)"))

        self.assertEqual(
            self.eval(u"(parse \"(+ 1 2)\")"),
            expected)

    def test_parse_invalid_parse(self):
        with self.assertRaises(ParseFailed):
            self.eval(u'(parse ")")')

    def test_parse_invalid_lex(self):
        with self.assertRaises(LexFailed):
            self.eval(u'(parse "123abc")')

    def test_parse_arg_number(self):
        with self.assertRaises(ArityError):
            self.eval(u"(parse)")

        with self.assertRaises(ArityError):
            self.eval(u'(parse "()" 1)')

    def test_parse_type_error(self):
        with self.assertRaises(TrifleTypeError):
            self.eval(u"(parse 123)")


class CallTest(BuiltInTestCase):
    def test_call_builtin_function(self):
        self.assertEqual(
            self.eval(u"(call + (quote (1 2 3)))"),
            Integer(6)
        )

    def test_call_function_with_env(self):
        self.assertEqual(
            self.eval(u"(call defined? (quote (x)))"),
            FALSE
        )

    def test_call_lambda_literal(self):
        self.assertEqual(
            self.eval(u"(call (lambda (x) x) (quote (1)))"),
            Integer(1)
        )

    def test_call_evals_once(self):
        """Ensure that `call` does not evaluate its arguments more than once.

        """
        self.assertEqual(
            self.eval(u"(call (lambda (x) x) (quote (y)))"),
            Symbol(u'y')
        )

    def test_call_arg_number(self):
        with self.assertRaises(ArityError):
            self.eval(u"(call + (quote (1 2 3)) 1)")

        with self.assertRaises(ArityError):
            self.eval(u"(call +)")

    def test_call_type(self):
        with self.assertRaises(TrifleTypeError):
            self.eval(u"(call #null (quote (1 2 3)))")

        with self.assertRaises(TrifleTypeError):
            self.eval(u"(call + #null)")


class EvalTest(BuiltInTestCase):
    def test_eval(self):
        self.assertEqual(
            self.eval(u"(eval (quote (+ 1 2 3)))"),
            Integer(6)
        )

    def test_eval_modifies_scope(self):
        self.assertEqual(
            self.eval(u'(set-symbol! (quote x) 0) (eval (quote (set-symbol! (quote x) 1))) x'),
            Integer(1)
        )


class EvaluatingMacrosTest(BuiltInTestCase):
    def test_macro(self):
        self.assertEqual(
            self.eval(u"(macro just-x (ignored-arg) (quote x)) (set-symbol! (quote x) 1) (just-x y)"),
            Integer(1)
        )

    def test_call_macro_too_few_args(self):
        with self.assertRaises(ArityError):
            self.eval(u"(macro ignore (x) #null) (ignore 1 2)")

    def test_call_macro_too_many_args(self):
        with self.assertRaises(ArityError):
            self.eval(u"(macro ignore (x) #null) (ignore)")

    # TODO: we shouldn't depend on the prelude here.
    # TODO: find a way to just call self.eval.
    def test_macro_rest_args(self):
        self.assertEqual(
            evaluate_all(parse(lex(
                u"(macro when (condition :rest body) (quote (if (unquote condition) (do (unquote* body)) #null)))"
                u"(set-symbol! (quote x) 1) (when #true (set-symbol! (quote x) 2)) x")), env_with_prelude()),
            Integer(2)
        )

    def test_macro_bad_args_number(self):
        with self.assertRaises(ArityError):
            self.eval(u"(macro foo)")

        with self.assertRaises(ArityError):
            self.eval(u"(macro foo (bar))")

    def test_macro_bad_arg_types(self):
        with self.assertRaises(TrifleTypeError):
            self.eval(u"(macro foo bar #null)")

        with self.assertRaises(TrifleTypeError):
            self.eval(u"(macro foo (1) #null)")

        with self.assertRaises(TrifleTypeError):
            self.eval(u"(macro 123 (bar) #null)")


class ExpandMacroTest(BuiltInTestCase):
    def test_expand_macro(self):
        self.assertEqual(
            self.eval(
                u"(macro just-x (ignored-arg) (quote x))"
                u"(expand-macro (just-x y))"),
            Symbol(u'x'))


class DefinedTest(BuiltInTestCase):
    def test_defined(self):
        self.assertEqual(
            self.eval(u"(defined? (quote +))"),
            TRUE)

        self.assertEqual(
            self.eval(u"(defined? (quote i-dont-exist))"),
            FALSE)

    def test_defined_type_error(self):
        with self.assertRaises(TrifleTypeError):
            self.eval(u"(defined? 1)")

    def test_defined_arity_error(self):
        with self.assertRaises(ArityError):
            self.eval(u"(defined?)")
            
        with self.assertRaises(ArityError):
            self.eval(u"(defined? (quote foo) 1)")


# TODO: error on nonexistent file, or file we can't read/write
# TODO: support read and write flags together
# TODO: add a seek! function
class OpenTest(BuiltInTestCase):
    def test_open_read(self):
        result = self.eval(u'(open "/etc/hosts" :read)')

        self.assertTrue(isinstance(result, FileHandle))

    def test_open_read_no_such_file(self):
        with self.assertRaises(FileNotFound):
            self.eval(u'(open "this_file_doesnt_exist" :read)')

    def test_open_write(self):
        result = self.eval(u'(open "/tmp/foo" :write)')

        self.assertTrue(isinstance(result, FileHandle))

    def test_open_invalid_flag(self):
        with self.assertRaises(TrifleValueError):
            self.eval(u'(open "/tmp/foo" :foo)')

    def test_open_arity_error(self):
        with self.assertRaises(ArityError):
            self.eval(u'(open "/foo/bar")')

        with self.assertRaises(ArityError):
            self.eval(u'(open "/foo/bar" :write :write)')

    def test_open_type_error(self):
        with self.assertRaises(TrifleTypeError):
            self.eval(u'(open "/foo/bar" #null)')

        with self.assertRaises(TrifleTypeError):
            self.eval(u"(open #null :write)")


class CloseTest(BuiltInTestCase):
    def test_close(self):
        result = self.eval(u'(set-symbol! (quote x) (open "/tmp/foo" :write)) (close! x) x')

        self.assertTrue(result.file_handle.closed)

    def test_close_twice_error(self):
        with self.assertRaises(UsingClosedFile):
            self.eval(u'(set-symbol! (quote x) (open "/tmp/foo" :write)) (close! x) (close! x)')

    def test_close_returns_null(self):
        result = self.eval(u'(close! (open "/tmp/foo" :write))')

        self.assertEqual(result, NULL)

    def test_close_arity_error(self):
        with self.assertRaises(ArityError):
            self.eval(u'(close! (open "/tmp/foo" :write) #null)')

        with self.assertRaises(ArityError):
            self.eval(u'(close!)')

    def test_close_type_error(self):
        with self.assertRaises(TrifleTypeError):
            self.eval(u'(close! #null)')


class ReadTest(BuiltInTestCase):
    def test_read(self):
        os.system('echo -n foo > test.txt')
        
        result = self.eval(u'(read (open "test.txt" :read))')

        os.remove('test.txt')

        self.assertEqual(
            result,
            Bytestring([ord(c) for c in "foo"]))

    def test_read_arity(self):
        with self.assertRaises(ArityError):
            self.eval(u"(read)")
            
        with self.assertRaises(ArityError):
            self.eval(u'(read "/etc/foo" :read :read)')
            
    def test_read_type_error(self):
        with self.assertRaises(TrifleTypeError):
            self.eval(u"(read #null)")


class WriteTest(BuiltInTestCase):
    def test_write(self):
        self.assertEqual(
            self.eval(
                u'(set-symbol! (quote f) (open "test.txt" :write))'
                u'(write! f (encode "foo")) (close! f)'),
            NULL)

        self.assertTrue(os.path.exists("test.txt"), "File was not created!")

        with open('test.txt') as f:
            self.assertEqual(f.read(), "foo")

        os.remove('test.txt')

    # todo: we should also test reading from a write-only handle.
    def test_write_read_only_handle(self):
        with self.assertRaises(ValueError):
            self.eval(
                u'(set-symbol! (quote f) (open "/etc/passwd" :read))'
                u'(write! f (encode "foo"))')

    def test_write_arity(self):
        # Too few args.
        with self.assertRaises(ArityError):
            self.eval(u'(write! (open "foo.txt" :write))')

        # Too many args.
        with self.assertRaises(ArityError):
            self.eval(u'(write! (open "foo.txt" :write) (encode "f") #null)')
            
    def test_write_type_error(self):
        with self.assertRaises(TrifleTypeError):
            self.eval(u'(write! #null (encode "f"))')

        with self.assertRaises(TrifleTypeError):
            self.eval(u'(write! (open "foo.txt" :write) #null)')

        os.remove('foo.txt')


class EncodeTest(BuiltInTestCase):
    def test_encode(self):
        self.assertEqual(
            self.eval(u'(encode "soufflé")'),
            Bytestring([ord(c) for c in b"souffl\xc3\xa9"]))
    
    def test_encode_type_error(self):
        with self.assertRaises(TrifleTypeError):
            self.eval(u'(encode #null)')
    
    def test_encode_arity_error(self):
        with self.assertRaises(ArityError):
            self.eval(u'(encode)')
    
        with self.assertRaises(ArityError):
            self.eval(u'(encode "foo" 2)')
    

class DecodeTest(BuiltInTestCase):
    def test_decode(self):
        self.assertEqual(
            self.eval(u'(decode #bytes("souffl\\xc3\\xa9"))'),
            String(list(u"soufflé")))

    def test_encode_type_error(self):
        with self.assertRaises(TrifleTypeError):
            self.eval(u'(decode #null)')
    
    def test_encode_arity_error(self):
        with self.assertRaises(ArityError):
            self.eval(u'(decode)')
    
        with self.assertRaises(ArityError):
            self.eval(u'(decode #bytes("souffl\\xc3\\xa9") 1)')
    

class ListPredicateTest(BuiltInTestCase):
    def test_is_list(self):
        self.assertEqual(
            self.eval(u'(list? (quote ()))'),
            TRUE)

    def test_is_not_list(self):
        self.assertEqual(
            self.eval(u'(list? #bytes(""))'),
            FALSE)

        self.assertEqual(
            self.eval(u'(list? #null)'),
            FALSE)

        self.assertEqual(
            self.eval(u'(list? 1.0)'),
            FALSE)

    def test_is_list_arity(self):
        with self.assertRaises(ArityError):
            self.eval(u'(list?)')

        with self.assertRaises(ArityError):
            self.eval(u'(list? #null #null)')


class StringPredicateTest(BuiltInTestCase):
    def test_is_string(self):
        self.assertEqual(
            self.eval(u'(string? "")'),
            TRUE)

    def test_is_not_string(self):
        self.assertEqual(
            self.eval(u'(string? #bytes(""))'),
            FALSE)

        self.assertEqual(
            self.eval(u'(string? #null)'),
            FALSE)

        self.assertEqual(
            self.eval(u'(string? 1.0)'),
            FALSE)

    def test_is_string_arity(self):
        with self.assertRaises(ArityError):
            self.eval(u'(string?)')

        with self.assertRaises(ArityError):
            self.eval(u'(string? #null #null)')


class BytestringPredicateTest(BuiltInTestCase):
    def test_is_bytestring(self):
        self.assertEqual(
            self.eval(u'(bytestring? #bytes(""))'),
            TRUE)

    def test_is_not_bytestring(self):
        self.assertEqual(
            self.eval(u'(bytestring? "")'),
            FALSE)

        self.assertEqual(
            self.eval(u'(bytestring? #null)'),
            FALSE)

        self.assertEqual(
            self.eval(u'(bytestring? 1.0)'),
            FALSE)

    def test_is_bytestring_arity(self):
        with self.assertRaises(ArityError):
            self.eval(u'(bytestring?)')

        with self.assertRaises(ArityError):
            self.eval(u'(bytestring? #null #null)')


class CharacterPredicateTest(BuiltInTestCase):
    def test_is_character(self):
        self.assertEqual(
            self.eval(u"(character? 'a')"),
            TRUE)

    def test_is_not_character(self):
        self.assertEqual(
            self.eval(u'(character? "")'),
            FALSE)

        self.assertEqual(
            self.eval(u'(character? #null)'),
            FALSE)

        self.assertEqual(
            self.eval(u'(character? 1.0)'),
            FALSE)

    def test_is_character_arity(self):
        with self.assertRaises(ArityError):
            self.eval(u'(character?)')

        with self.assertRaises(ArityError):
            self.eval(u'(character? #null #null)')


class ExitTest(BuiltInTestCase):
    def test_exit(self):
        with self.assertRaises(SystemExit):
            self.eval(u'(exit!)')


class TryTest(BuiltInTestCase):
    def test_try_with_matching_error(self):
        """If an error occurs, we should evaluate the catch block if it
        matches.

        """
        self.assertEqual(
            self.eval(u"(try (/ 1 0) :catch (zero-division-error #null))"),
            NULL)

    def test_try_without_matching_error(self):
        """If an error occurs, we should not evaluate the catch block if it
        does not match.

        """
        with self.assertRaises(ZeroDivisionError):
            self.eval(u"(try (/ 1 0) :catch (no-such-variable-error #null))")

    def test_try_without_error(self):
        """If no error occurs, we should not evaluate the catch block.

        """
        self.assertEqual(
            self.eval(u"(try 1 :catch (no-such-variable-error #null))"),
            Integer(1))

    def test_try_arity(self):
        # TODO: support multiple catch statements

        # Too few arguments.
        with self.assertRaises(ArityError):
            self.eval(u"(try x :catch)")

        # Too many arguments.
        with self.assertRaises(ArityError):
            self.eval(u"(try x :catch (zero-division-error #null) #null)")

        # Too few arguments in catch.
        with self.assertRaises(ArityError):
            self.eval(u"(try x :catch (zero-division-error) #null)")

    def test_catch_error_propagates(self):
        """If an error occurs during the evaluation of the catch block, it
        should propagate as usual.

        """
        with self.assertRaises(UnboundVariable):
            self.eval(u"(try (/ 1 0) :catch (zero-division-error x))")

    def test_try_types(self):
        with self.assertRaises(TrifleTypeError):
            self.eval(u"(try (/ 1 0) :catch #null)")
            
        with self.assertRaises(TrifleTypeError):
            self.eval(u"(try (/ 1 0) #null (zero-division-error #null))")
