# -*- coding: utf-8 -*-
import unittest
import os

from rpython.rlib.rbigint import rbigint as RBigInt

from mock import patch, Mock

from interpreter.lexer import lex
from interpreter.trifle_parser import parse_one, parse
from interpreter.built_ins import Add, SetSymbol, If
from interpreter.trifle_types import (
    Hashmap, List, Integer, Float, Fraction,
    Symbol, Keyword, String, Character,
    Lambda, Boolean,
    TRUE, FALSE, NULL,
    FileHandle, Bytestring,
    TrifleExceptionInstance)
from interpreter.evaluator import evaluate, is_thrown_exception
from interpreter.errors import (
    error, lex_failed, parse_failed, missing_key,
    file_not_found, value_error, stack_overflow,
    division_by_zero, wrong_type, no_such_variable,
    changing_closed_handle, wrong_argument_number)
from interpreter.environment import Environment, Scope, fresh_environment

"""Trifle unit tests. These are intended to be run with CPython, and
no effort has been made to make them RPython friendly.

"""

class BuiltInTestCase(unittest.TestCase):
    def eval(self, program, env=None):
        """Evaluate this program in a fresh environment. Returns the result of
        the last expression.

        """
        assert isinstance(program, unicode), "Source code must be unicode, not %s." % type(program)

        parse_tree = parse(lex(program))
        if isinstance(parse_tree, TrifleExceptionInstance):
            self.fail("Parse error on: %r" % program)

        if env is None:
            env = fresh_environment()
        
        result = NULL
        for expression in parse_tree.values:
            result = evaluate(expression, env)

            if is_thrown_exception(result, error):
                return result

        return result

    # TODO: It'd be clearer to remove this, requiring callers to use
    # .eval and .assertTrifleError instead.
    def assertEvalError(self, program, error_type):
        """Assert that this program raises an error of type error_type when
        executed.

        """
        result = self.eval(program)
        self.assertTrifleError(result, error_type)

    def assertTrifleError(self, value, expected_error_type):
        """Assert that this value is a thrown error of the expected type.

        """
        self.assertTrue(isinstance(value, TrifleExceptionInstance),
                        "Expected an error, but got: %s" % value.repr())

        self.assertEqual(value.exception_type, expected_error_type,
                         "Expected %s, but got %s" %
                         (expected_error_type.name, value))

        self.assertFalse(value.caught, "Expected a thrown exception, but this exception has been caught!")


class LexTestCase(unittest.TestCase):
    def assertLexResult(self, program, expected):
        """Assert that program, when lexed, returns a Trifle type equal to
        expected.

        Assumes that program is a single expression.

        """
        result = lex(program)

        if not isinstance(result, List):
            self.fail("Lexing failed: %r" % result)

        self.assertEqual(result.values[0], expected)


class CommentLexTest(BuiltInTestCase):
    def test_lex_comment(self):
        self.assertEqual(
            lex(u"1 ; 2 \n 3"), List([Integer.fromint(1), Integer.fromint(3)]))


class IntegerLexTest(BuiltInTestCase, LexTestCase):
    def test_lex_positive_number(self):
        self.assertLexResult(u"123", Integer.fromint(123))

        self.assertLexResult(u"0123", Integer.fromint(123))

    def test_lex_negative_number(self):
        self.assertLexResult(u"-123", Integer.fromint(-123))

    def test_lex_number_with_underscores(self):
        self.assertLexResult(u"1_000", Integer.fromint(1000))

    def test_lex_zero(self):
        self.assertLexResult(u"0", Integer.fromint(0))

        self.assertLexResult(u"-0", Integer.fromint(0))

    def test_lex_invalid_number(self):
        self.assertTrifleError(
            lex(u"123abc"), lex_failed)


class FloatLexTest(BuiltInTestCase, LexTestCase):
    def test_lex_positive(self):
        self.assertLexResult(u"123.0", Float(123.0))

    def test_lex_float_leading_zero(self):
        self.assertLexResult(u"0123.0", Float(123.0))

    def test_lex_negative(self):
        self.assertLexResult(u"-123.0", Float(-123.0))

    def test_lex_with_underscores(self):
        self.assertLexResult(u"1_000.000_2", Float(1000.0002))
        

    def test_lex_invalid(self):
        self.assertTrifleError(
            lex(u"123.abc"), lex_failed)

        self.assertTrifleError(
            lex(u"123.456abc"), lex_failed)


class FractionLexTest(BuiltInTestCase, LexTestCase):
    def test_lex_fraction(self):
        self.assertLexResult(u"1/3", Fraction(RBigInt.fromint(1), RBigInt.fromint(3)))

    def test_lex_fraction_underscore(self):
        self.assertLexResult(u"1/3_0", Fraction(RBigInt.fromint(1), RBigInt.fromint(30)))

    def test_lex_fraction_to_integer(self):
        self.assertLexResult(u"2/1", Integer.fromint(2))
        self.assertLexResult(u"3/3", Integer.fromint(1))

    def test_lex_fraction_zero_denominator(self):
        self.assertTrifleError(
            lex(u"1/0"), division_by_zero)

    def test_lex_fraction_not_simplified(self):
        self.assertLexResult(u"2/6", Fraction(RBigInt.fromint(1), RBigInt.fromint(3)))

    def test_lex_invalid_fraction(self):
        self.assertTrifleError(
            lex(u"1/3/4"), lex_failed)


class SymbolLexTest(BuiltInTestCase, LexTestCase):
    def test_lex_symbol(self):
        self.assertLexResult(u"x", Symbol(u'x'))

        self.assertLexResult(u"x1", Symbol(u'x1'))

        self.assertLexResult(u"foo?", Symbol(u'foo?'))

        self.assertLexResult(u"foo!", Symbol(u'foo!'))

        self.assertLexResult(u"foo_bar", Symbol(u'foo_bar'))

        self.assertLexResult(u"FOOBAR", Symbol(u'FOOBAR'))

        self.assertLexResult(u"<=", Symbol(u'<='))

        self.assertLexResult(u"_", Symbol(u'_'))

    def test_lex_invalid_symbol(self):
        self.assertTrifleError(
            lex(u"\\"), lex_failed)


class KeywordLexTest(BuiltInTestCase, LexTestCase):
    def test_lex_keyword(self):
        self.assertLexResult(u":x", Keyword(u'x'))

    def test_lex_invalid_keyword(self):
        self.assertTrifleError(
            lex(u":123"), lex_failed)


class HashmapParseTest(BuiltInTestCase, LexTestCase):
    def test_parse_empty_hashmap(self):
        self.assertEqual(parse_one(lex(u"{}")),
                         Hashmap())

    def test_parse_hashmap(self):
        expected = Hashmap()
        expected.dict[Integer.fromint(1)] = Integer.fromint(2)
        expected.dict[Integer.fromint(3)] = Integer.fromint(4)
        
        self.assertEqual(parse_one(lex((u"{1 2 3 4}"))), expected)

    # TODOC the ability to use commas.
    def test_parse_hashmap_comma(self):
        expected = Hashmap()
        expected.dict[Integer.fromint(1)] = Integer.fromint(2)
        expected.dict[Integer.fromint(3)] = Integer.fromint(4)
        
        self.assertEqual(parse_one(lex(u"{1 2, 3 4}")), expected)
        
    def test_hashmap_mismatched_curly_parens(self):
        self.assertTrifleError(
            parse_one(lex(u"{")), parse_failed)

        self.assertTrifleError(
            parse_one(lex(u"}")), parse_failed)

        self.assertTrifleError(
            parse_one(lex(u"(}")), parse_failed)

        self.assertTrifleError(
            parse_one(lex(u"{)")), parse_failed)

    def test_hashmap_odd_number_elements(self):
        self.assertTrifleError(
            parse_one(lex(u"{1}")), parse_failed)

        self.assertTrifleError(
            parse_one(lex(u"{1 2 3}")), parse_failed)

        self.assertTrifleError(
            parse_one(lex(u"(1 {2})")), parse_failed)

    def test_hashmap_duplicate_keys(self):
        # Silly, but harmless. Last one wins.
        expected = Hashmap()
        expected.dict[Integer.fromint(1)] = Integer.fromint(3)
        
        self.assertEqual(parse_one(lex(u"{1 2, 1 3}")), expected)

    def test_hashmap_unhashable_keys(self):
        # TODO: add immutable strings.
        self.assertTrifleError(
            parse_one(lex(u'{"foo" 1}')), wrong_type)

        
class StringLexTest(BuiltInTestCase, LexTestCase):
    def test_lex_string(self):
        self.assertLexResult(u'"foo"', String(list(u'foo')))

        self.assertLexResult(u'"foo\nbar"', String(list(u'foo\nbar')))

        self.assertLexResult(u'"foo,"', String(list(u'foo,')))

    def test_lex_non_ascii_string(self):
        self.assertLexResult(u'"flambé"', String(list(u'flambé')))

    def test_lex_backslash(self):
        # Backslashes should be an error if not escaped.
        self.assertTrifleError(
            lex(u'"\\"'), lex_failed)

        self.assertLexResult(u'"\\\\"', String(list(u'\\')))

    def test_lex_newline(self):
        self.assertLexResult(u'"\n"', String(list(u'\n')))

        self.assertLexResult(u'"\\n"', String(list(u'\n')))

    def test_lex_escaped_quote(self):
        self.assertLexResult(u'"\\""', String(list(u'"')))


class CharacterLexTest(BuiltInTestCase, LexTestCase):
    def test_lex_character(self):
        self.assertLexResult(u"'a'", Character(u'a'))

    def test_lex_non_ascii_character(self):
        self.assertLexResult(u"'é'", Character(u'é'))

    def test_lex_backslash(self):
        # Backslashes should be an error if not escaped.
        self.assertTrifleError(
            lex(u"'\\'"), lex_failed)

        self.assertLexResult(u"'\\\\'", Character(u'\\'))

    def test_lex_newline(self):
        self.assertLexResult(u"'\n'", Character(u'\n'))

        self.assertLexResult(u"'\\n'", Character(u'\n'))

    def test_lex_escaped_quote(self):
        self.assertLexResult(u"'\\''", Character(u"'"))


class BytestringLexTest(BuiltInTestCase, LexTestCase):
    def test_lex_bytestring(self):
        self.assertLexResult(u'#bytes("foo")', Bytestring([ord(c) for c in 'foo']))

    def test_lex_multiple_bytestrings(self):
        self.assertEqual(
            lex(u'#bytes("foo") #bytes("bar")').values[1],
            Bytestring([ord(c) for c in 'bar']))

    def test_lex_invalid_byte(self):
        self.assertTrifleError(
            lex(u'#bytes("flambé")'), lex_failed)

    def test_lex_backslash(self):
        # Backslashes should be an error if not escaped.
        self.assertTrifleError(
            lex(u'#bytes("\\")'), lex_failed)

        self.assertLexResult(u'#bytes("\\\\")', Bytestring([ord('\\')]))

    def test_lex_escaped_byte(self):
        self.assertLexResult(u'#bytes("\\xff")', Bytestring([255]))

        self.assertLexResult(u'#bytes("\\xFF")', Bytestring([255]))

    def test_lex_invalid_escaped_byte(self):
        # Not hexadecimal characters:
        self.assertTrifleError(
            lex(u'#bytes("\\xgg")'), lex_failed)

        # Not starting with \x
        self.assertTrifleError(
            lex(u'#bytes("\\yff")'), lex_failed)

        # Insufficient characters:
        self.assertTrifleError(
            lex(u'#bytes("\\xa")'), lex_failed)
        self.assertTrifleError(
            lex(u'#bytes("\\x")'), lex_failed)
            
        # Insufficient characters before next escaped character:
        self.assertTrifleError(
            lex(u'#bytes("\\xa\\xaa")'), lex_failed)


class BooleanLexTest(BuiltInTestCase, LexTestCase):
    def test_lex_boolean(self):
        self.assertLexResult(u"#true", TRUE)

        self.assertLexResult(u"#false", FALSE)

    def test_lex_symbol_leading_bool(self):
        """Ensure that a literal whose prefix is a valid boolean, is still a
        lex error.

        """
        self.assertTrifleError(
            lex(u"#trueish"), lex_failed)


class NullLexTest(BuiltInTestCase, LexTestCase):
    def test_lex_boolean(self):
        self.assertLexResult(u"#null", NULL)


class ParsingTest(BuiltInTestCase):
    def test_parse_list(self):
        self.assertEqual(parse_one(lex(u"(1 2)")),
                         List([Integer.fromint(1), Integer.fromint(2)]))

    def test_parse_list_with_commas(self):
        self.assertEqual(parse_one(lex(u"(1, 2, 3,)")),
                         List([Integer.fromint(1), Integer.fromint(2),
                               Integer.fromint(3)]))


class EvaluatingTypesTest(BuiltInTestCase):
    # TODO: this should be a syntax error.
    def test_eval_empty_list(self):
        self.assertTrifleError(
            self.eval(u"()"), value_error)

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
            Integer.fromint(123))

    def test_eval_float(self):
        self.assertEqual(
            self.eval(u"123.4"),
            Float(123.4))

    def test_eval_fraction(self):
        self.assertEqual(
            self.eval(u"1/4"),
            Fraction(RBigInt.fromint(1), RBigInt.fromint(4)))

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

    def test_eval_exception_type(self):
        self.assertEqual(
            self.eval(u"error"),
            error)

    def test_eval_exception_instance(self):
        result = self.eval(u"(try x :catch no-such-variable e e)")
        self.assertTrue(isinstance(result, TrifleExceptionInstance))

    def test_eval_function(self):
        result = self.eval(u"(lambda (x) x)")
        self.assertTrue(isinstance(result, Lambda))


class ReprTest(BuiltInTestCase):
    def test_list_repr(self):
        list_val = List([Integer.fromint(1)])
        self.assertEqual(list_val.repr(), '(1)')

    def test_hashmap_repr(self):
        hashmap_val = Hashmap()
        hashmap_val.dict[Integer.fromint(1)] = Integer.fromint(2)
        hashmap_val.dict[Integer.fromint(3)] = Integer.fromint(4)
        self.assertEqual(hashmap_val.repr(), '{1 2, 3 4}')

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
        val = Integer.fromint(12)
        self.assertEqual(val.repr(), '12')

    def test_big_integer_repr(self):
        val = Integer.fromstr("12345678901234567890")
        self.assertEqual(val.repr(), '12345678901234567890')

    def test_fraction_repr(self):
        val = Fraction(RBigInt.fromint(1), RBigInt.fromint(12))
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

    def test_error_type_repr(self):
        # TODO: unit test error instances too.
        self.assertEqual(division_by_zero.repr(), '#error-type("division-by-zero")')

    def test_built_in_function_repr(self):
        self.assertEqual(SetSymbol().repr(), u"<built-in function>")
        self.assertEqual(Add().repr(), u"<built-in function>")

    def test_built_special_repr(self):
        self.assertEqual(If().repr(), u"<special expression>")


class EvaluatingLambdaTest(BuiltInTestCase):
    def test_call_lambda(self):
        self.assertEqual(
            self.eval(u"((lambda (x) x) 1)"),
            Integer.fromint(1))

    def test_call_lambda_last_value(self):
        self.assertEqual(
            self.eval(u"((lambda () 1 2))"),
            Integer.fromint(2))

    def test_call_not_lambda(self):
        self.assertEvalError(
            u"(1)", wrong_type)

        self.assertEvalError(
            u"(#null)", wrong_type)

        self.assertEvalError(
            u'("a")', wrong_type)
    
        self.assertEvalError(
            u'((quote (1)))', wrong_type)
    
    def test_call_lambda_variable_arguments(self):
        expected = List([Integer.fromint(1), Integer.fromint(2), Integer.fromint(3), Integer.fromint(4)])
        
        self.assertEqual(
            self.eval(u"((lambda (:rest args) args) 1 2 3 4)"),
            expected)

    def test_call_lambda_too_few_arguments(self):
        self.assertEvalError(
            u"((lambda (x) 1))", wrong_argument_number)

    def test_call_lambda_too_few_variable_arguments(self):
        self.assertEvalError(
            u"((lambda (x y :rest args) x))", wrong_argument_number)

    def test_call_lambda_too_many_arguments(self):
        self.assertEvalError(
            u"((lambda () 1) 2)", wrong_argument_number)

    def test_lambda_wrong_arg_number(self):
        self.assertEvalError(
            u"(lambda)", wrong_argument_number)

    def test_lambda_params_not_list(self):
        self.assertEvalError(
            u"(lambda foo bar)", wrong_type)

    def test_lambda_params_not_symbols(self):
        self.assertEvalError(
            u"(lambda (1 2) bar)", wrong_type)

    def test_evaluate_lambda(self):
        lambda_obj = self.eval(u"(lambda (x) x)")

        self.assertTrue(isinstance(lambda_obj, Lambda),
                        "Expected a lambda object but got a %s" % lambda_obj.__class__)

    def test_call_lambda_repeated_args(self):
        # TODO: this should be a syntax error
        # TODO: ideally this would happen without calling the lambda
        self.assertEvalError(
            u"((lambda (x x) 1) 1 2)",
            value_error)

    def test_lambda_scope_doesnt_leak(self):
        """Ensure that defining a variable inside a lambda is accessible
        inside the body, but doesn't leak outside.

        """
        self.assertEqual(
            self.eval(u"((lambda () (set-symbol! (quote x) 2) x))"),
            Integer.fromint(2))

        self.assertEvalError(
            u"((lambda () (set-symbol! (quote x) 2)) x)", no_such_variable)

    def test_closure_variables(self):
        """Ensure that we can update closure variables inside a lambda.

        """
        self.assertEqual(
            self.eval(u"(set-symbol! (quote x) 1) ((lambda () (set-symbol! (quote x) 2))) x"),
            Integer.fromint(2))

    # TODO: also test for stack overflow inside macros.
    def test_stack_overflow(self):
        self.assertEvalError(
            u"(set-symbol! (quote f) (lambda () (f))) (f)", stack_overflow)


class FreshSymbolTest(BuiltInTestCase):
    def test_fresh_symbol(self):
        self.assertEqual(
            self.eval(u"(fresh-symbol)"),
            Symbol(u"1-unnamed"))

    def test_fresh_symbol_wrong_arg_number(self):
        self.assertEvalError(
            u"(fresh-symbol 1)", wrong_argument_number)


class SetSymbolTest(BuiltInTestCase):
    def test_set_symbol(self):
        self.assertEqual(
            self.eval(u"(set-symbol! (quote x) (quote y)) x"),
            Symbol(u"y"))

    def test_set_symbol_wrong_arg_number(self):
        self.assertEvalError(
            u"(set-symbol! (quote x) 1 2)", wrong_argument_number)

    def test_set_symbol_returns_null(self):
        self.assertEqual(
            self.eval(u"(set-symbol! (quote x) 1)"),
            NULL)

    def test_set_symbol_first_arg_symbol(self):
        self.assertEvalError(
            u"(set-symbol! 1 2)", wrong_type)


class LetTest(BuiltInTestCase):
    def test_let(self):
        self.assertEqual(
            self.eval(u"(let (x 1) x)"),
            Integer.fromint(1))

    def test_let_access_previous_bindings(self):
        self.assertEqual(
            self.eval(u"(let (x 1 y (+ x 1)) y)"),
            Integer.fromint(2))

    def test_let_malformed_bindings(self):
        self.assertEvalError(
            u"(let (1 1) #null)", wrong_type)

    def test_let_odd_bindings(self):
        self.assertEvalError(
            u"(let (x 1 y) #null)", wrong_argument_number)

    def test_let_not_bindings(self):
        # TODO: these should probably both be syntax errors.
        self.assertEvalError(
            u"(let #null #null)", wrong_type)

        self.assertEvalError(
            u"(let)", wrong_argument_number)

    def test_let_shadowing(self):
        """Ensure that variables defined in a let shadow outer variables with
        the same name.

        """
        self.assertEqual(
            self.eval(u"(set-symbol! (quote x) 1) (let (x 2) (set-symbol! (quote x) 3)) x"),
            Integer.fromint(1))

    def test_let_variables_dont_leak(self):
        """Ensure that variables defined in a let are undefined in the global scope.
        Regression test for the first variable in the bindings.

        """
        self.assertEvalError(
            u"(let (x 1 y 2) #null) x", no_such_variable)

    def test_let_not_function_scope(self):
        """Ensure that variables defined with set! are still available outside
        a let.

        """
        self.assertEqual(
            self.eval(u"(let () (set-symbol! (quote x) 3)) x"),
            Integer.fromint(3))


class QuoteTest(BuiltInTestCase):
    def test_quote(self):
        expected = parse_one(lex(u"(+ 1 2)"))
        
        self.assertEqual(
            self.eval(u"(quote (+ 1 2))"),
            expected)

    def test_quote_fresh_copy(self):
        self.assertEqual(
            self.eval(
                u"(set-symbol! (quote new-list) (lambda () (quote ())))"
                u"(insert! (new-list) 0 1)"
                u"(new-list)"
            ), List())

    def test_quote_wrong_number_args(self):
        self.assertEvalError(
            u"(quote foo bar)", wrong_argument_number)

        self.assertEvalError(
            u"(quote)", wrong_argument_number)

    def test_unquote(self):
        self.assertEqual(
            self.eval(u"(quote (unquote (+ 1 2)))"),
            Integer.fromint(3))

    def test_unquote_nested(self):
        expected = List([Symbol(u'x'), Integer.fromint(1)])
        
        self.assertEqual(
            self.eval(u"(set-symbol! (quote x) 1) (quote (x (unquote x)))"),
            expected)

    def test_unquote_star(self):
        expected = parse_one(lex(u"(baz foo bar)"))
        
        self.assertEqual(
            self.eval(u"(set-symbol! (quote x) (quote (foo bar))) (quote (baz (unquote* x)))"),
            expected)

    def test_unquote_wrong_arg_number(self):
        self.assertEvalError(
            u"(set-symbol! (quote x) 1) (quote (unquote x x))", wrong_argument_number)

        self.assertEvalError(
            u"(quote (unquote))", wrong_argument_number)

    def test_unquote_star_wrong_arg_number(self):
        self.assertEvalError(
            u"(set-symbol! (quote x) 1) (quote (list (unquote* x x)))", wrong_argument_number)

        self.assertEvalError(
            u"(quote (list (unquote*)))", wrong_argument_number)

    def test_unquote_star_wrong_type(self):
        self.assertEvalError(
            u"(quote (list (unquote* 1)))", wrong_type)

    def test_unquote_star_top_level(self):
        self.assertEvalError(
            u"(quote (unquote* #null))", value_error)

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
                         Integer.fromint(0))
        
        self.assertEqual(self.eval(u"(+ 1)"),
                         Integer.fromint(1))
        
        self.assertEqual(self.eval(u"(+ 1 2)"),
                         Integer.fromint(3))

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
                         Fraction(RBigInt.fromint(5), RBigInt.fromint(6)))
        
        self.assertEqual(self.eval(u"(+ 1 1/2)"),
                         Fraction(RBigInt.fromint(3), RBigInt.fromint(2)))
        
        self.assertEqual(self.eval(u"(+ 3/2 1/2)"),
                         Integer.fromint(2))
        
    def test_invalid_type(self):
        self.assertEvalError(
            u"(+ +)", wrong_type)


class SubtractTest(BuiltInTestCase):
    def test_subtract(self):
        self.assertEqual(self.eval(u"(-)"),
                         Integer.fromint(0))
        
        self.assertEqual(self.eval(u"(- 1)"),
                         Integer.fromint(-1))
        
        self.assertEqual(self.eval(u"(- 5 2)"),
                         Integer.fromint(3))

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
                         Fraction(RBigInt.fromint(-1), RBigInt.fromint(2)))

        self.assertEqual(self.eval(u"(- 1/2 1/4)"),
                         Fraction(RBigInt.fromint(1), RBigInt.fromint(4)))

        self.assertEqual(self.eval(u"(- 3/2 1/2)"),
                         Integer.fromint(1))

    def test_invalid_type(self):
        self.assertEvalError(
            u"(- -)", wrong_type)


class MultiplyTest(BuiltInTestCase):
    def test_multiply(self):
        self.assertEqual(self.eval(u"(*)"),
                         Integer.fromint(1))
        
        self.assertEqual(self.eval(u"(* 2)"),
                         Integer.fromint(2))
        
        self.assertEqual(self.eval(u"(* 2 3)"),
                         Integer.fromint(6))

    def test_multiply_floats(self):
        self.assertEqual(self.eval(u"(* 2.0 3.0)"),
                         Float(6.0))
        
        self.assertEqual(self.eval(u"(* 2 3.0)"),
                         Float(6.0))

        self.assertEqual(self.eval(u"(* 1/2 1.0)"),
                         Float(0.5))

    def test_multiply_fractions(self):
        self.assertEqual(self.eval(u"(* 1/2 3/5)"),
                         Fraction(RBigInt.fromint(3), RBigInt.fromint(10)))
        
        self.assertEqual(self.eval(u"(* 1/3 2)"),
                         Fraction(RBigInt.fromint(2), RBigInt.fromint(3)))
        
        self.assertEqual(self.eval(u"(* 2 1/2)"),
                         Integer.fromint(1))

    def test_invalid_type(self):
        self.assertEvalError(
            u"(* 1 #null)", wrong_type)


class DivideTest(BuiltInTestCase):
    def test_divide(self):
        self.assertEqual(self.eval(u"(/ 1 2)"),
                         Fraction(RBigInt.fromint(1), RBigInt.fromint(2)))

        self.assertEqual(self.eval(u"(/ 1 2 2)"),
                         Fraction(RBigInt.fromint(1), RBigInt.fromint(4)))

    def test_divide_floats(self):
        self.assertEqual(self.eval(u"(/ 1.0 2)"),
                         Float(0.5))
        
        self.assertEqual(self.eval(u"(/ 1.0 1/2)"),
                         Float(2.0))
        
    def test_divide_fractions(self):
        self.assertEqual(self.eval(u"(/ 1/2 1/3)"),
                         Fraction(RBigInt.fromint(3), RBigInt.fromint(2)))
        
        self.assertEqual(self.eval(u"(/ 1/2 1/2)"),
                         Integer.fromint(1))
        
    def test_divide_by_zero(self):
        result = self.eval(u"(/ 1 0)")
        self.assertTrue(isinstance(result, TrifleExceptionInstance))
            
        result = self.eval(u"(/ 1.0 0.0)")
        self.assertTrue(isinstance(result, TrifleExceptionInstance))
            
    def test_invalid_type(self):
        self.assertEvalError(
            u"(/ 1 #null)", wrong_type)

    def test_arity_error(self):
        self.assertEvalError(
            u"(/ 1)", wrong_argument_number)


class ModTest(BuiltInTestCase):
    def test_mod(self):
        self.assertEqual(self.eval(u"(mod 11 10)"),
                         Integer.fromint(1))

    def test_mod_by_zero(self):
        self.assertEvalError(
            u"(mod 1 0)", division_by_zero)

    def test_invalid_type(self):
        self.assertEvalError(
            u"(mod 1 #null)", wrong_type)

        self.assertEvalError(
            u"(mod 1 0.5)", wrong_type)

    def test_arity_error(self):
        self.assertEvalError(
            u"(mod 1)", wrong_argument_number)

        self.assertEvalError(
            u"(mod 1 2 3)", wrong_argument_number)


class DivTest(BuiltInTestCase):
    def test_div(self):
        self.assertEqual(self.eval(u"(div 5 2)"),
                         Integer.fromint(2))

        self.assertEqual(self.eval(u"(div -5 2)"),
                         Integer.fromint(-3))

    def test_div_by_zero(self):
        self.assertEvalError(
            u"(div 1 0)", division_by_zero)

    def test_invalid_type(self):
        self.assertEvalError(
            u"(div 1 #null)", wrong_type)

        self.assertEvalError(
            u"(div 2.0 1.0)", wrong_type)

    def test_arity_error(self):
        self.assertEvalError(
            u"(div 1)", wrong_argument_number)

        self.assertEvalError(
            u"(div 1 2 3)", wrong_argument_number)


class IfTest(BuiltInTestCase):
    def test_if(self):
        self.assertEqual(
            self.eval(u"(if #true 2 3)"),
            Integer.fromint(2))

        self.assertEqual(
            self.eval(u"(if #false 4 5)"),
            Integer.fromint(5))

    def test_if_type_error(self):
        self.assertEvalError(
            u"(if 1 2 3)", wrong_type)

    def test_if_two_args_evals_condition(self):
        self.assertEqual(
            self.eval(u"(set-symbol! (quote x) #false) (if x 2 3)"),
            Integer.fromint(3))

    def test_if_wrong_number_of_args(self):
        self.assertEvalError(
            u"(if #true)", wrong_argument_number)

        self.assertEvalError(
            u"(if 1 2 3 4)", wrong_argument_number)


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
            Integer.fromint(2))
        
    def test_while_wrong_number_of_args(self):
        self.assertEvalError(
            u"(while)", wrong_argument_number)

    def test_while_type_error(self):
        self.assertEvalError(
            u"(while 1 (foo))", wrong_type)


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
        self.assertEvalError(
            u"(input 1)", wrong_type)

    def test_input_arity_error(self):
        self.assertEvalError(
            u"(input)", wrong_argument_number)

        self.assertEvalError(
            u"(input \"foo\" 1)", wrong_argument_number)


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

        self.assertEqual(
            self.eval(u"(same? #true (quote foo))"),
            FALSE)

        self.assertEqual(
            self.eval(u"(same? #true (quote ()))"),
            FALSE)

        self.assertEqual(
            self.eval(u"(same? (quote foo) #true)"),
            FALSE)

    def test_same_wrong_number_of_args(self):
        self.assertEvalError(
            u"(same? 1)", wrong_argument_number)

        self.assertEvalError(
            u"(same? 1 2 3)", wrong_argument_number)


class EqualTest(BuiltInTestCase):
    def test_booleans_equal(self):
        self.assertEqual(
            self.eval(u"(equal? #true #true)"),
            TRUE)

        self.assertEqual(
            self.eval(u"(equal? #false #false)"),
            TRUE)

    def test_fresh_booleans_equal(self):
        """Ensure that we treat booleans as equal even if they aren't the same
        instance. This is for robustness, functions should avoid doing this.

        """
        env = fresh_environment()
        env.set(u'true1', Boolean(True))
        env.set(u'true2', Boolean(True))
        env.set(u'false1', Boolean(False))
        env.set(u'false2', Boolean(False))
        
        self.assertEqual(
            self.eval(u"(equal? true1 true2)", env),
            TRUE)

        self.assertEqual(
            self.eval(u"(equal? false1 false2)", env),
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

    def test_fractions_same(self):
        self.assertEqual(
            self.eval(u"(equal? 1/2 2/4)"),
            TRUE)

        self.assertEqual(
            self.eval(u"(equal? 1/2 0.5)"),
            TRUE)

        self.assertEqual(
            self.eval(u"(equal? 1/1 1)"),
            TRUE)

    def test_numbers_same(self):
        self.assertEqual(
            self.eval(u"(equal? 1.0 1)"),
            TRUE)

        self.assertEqual(
            self.eval(u"(equal? 1 1.0)"),
            TRUE)

        self.assertEqual(
            self.eval(u"(equal? 1 1/1)"),
            TRUE)

    def test_null_equal(self):
        self.assertEqual(
            self.eval(u"(equal? #null #null)"),
            TRUE)

    def test_symbol_equal(self):
        self.assertEqual(
            self.eval(u"(equal? (quote a) (quote a))"),
            TRUE)

    def test_keywords_equal(self):
        self.assertEqual(
            self.eval(u"(equal? :x :x)"),
            TRUE)

        self.assertEqual(
            self.eval(u"(equal? :x :y)"),
            FALSE)

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

        # Different types.
        self.assertEqual(
            self.eval(u"(equal? (quote ()) #null)"),
            FALSE)

    def test_hashmaps_equal(self):
        # Equal
        self.assertEqual(
            self.eval(u"(equal? {1 2} {1 2})"),
            TRUE)

        # Same length, different values.
        self.assertEqual(
            self.eval(u"(equal? {1 2} {1 3})"),
            FALSE)

        # Different lengths.
        self.assertEqual(
            self.eval(u"(equal? {1 2} {1 2, 3 4})"),
            FALSE)

        # Different types.
        self.assertEqual(
            self.eval(u"(equal? {1 2} #null)"),
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
        self.assertEvalError(
            u"(equal? 1)", wrong_argument_number)

        self.assertEvalError(
            u"(equal? 1 2 3)", wrong_argument_number)


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
        self.assertEvalError(
            u"(< #true #false)", wrong_type)

    def test_less_than_insufficient_args(self):
        self.assertEvalError(
            u"(<)", wrong_argument_number)

        self.assertEvalError(
            u"(< 1)", wrong_argument_number)


class LengthTest(BuiltInTestCase):
    def test_length_list(self):
        self.assertEqual(
            self.eval(u"(length (quote (2 3)))"),
            Integer.fromint(2))

    def test_length_list_string(self):
        self.assertEqual(
            self.eval(u'(length "abc")'),
            Integer.fromint(3))

    def test_length_bytestring(self):
        self.assertEqual(
            self.eval(u'(length #bytes("abc"))'),
            Integer.fromint(3))

    def test_length_typeerror(self):
        self.assertEvalError(
            u"(length 1)", wrong_type)
            
    def test_length_arg_number(self):
        self.assertEvalError(
            u"(length)", wrong_argument_number)
            
        self.assertEvalError(
            u"(length (quote ()) 1)", wrong_argument_number)
            

class GetIndexTest(BuiltInTestCase):
    def test_get_index_list(self):
        self.assertEqual(
            self.eval(u"(get-index (quote (2 3)) 0)"),
            Integer.fromint(2))

    def test_get_index_bytestring(self):
        self.assertEqual(
            self.eval(u'(get-index #bytes("abc") 0)'),
            Integer.fromint(97))

    def test_get_index_string(self):
        self.assertEqual(
            self.eval(u'(get-index "abc" 0)'),
            Character(u'a'))

    def test_get_index_negative_index(self):
        self.assertEqual(
            self.eval(u"(get-index (quote (2 3)) -1)"),
            Integer.fromint(3))

    def test_get_index_negative_index_error(self):
        self.assertEvalError(
            u"(get-index (quote (2 3)) -3)", value_error)

    def test_get_index_typeerror(self):
        self.assertEvalError(
            u"(get-index #null 0)", wrong_type)

        self.assertEvalError(
            u"(get-index (quote (1)) #false)", wrong_type)

    def test_get_index_indexerror(self):
        self.assertEvalError(
            u"(get-index (quote ()) 0)", value_error)

        self.assertEvalError(
            u"(get-index (quote (1)) 2)", value_error)

    def test_get_index_wrong_arg_number(self):
        self.assertEvalError(
            u"(get-index)", wrong_argument_number)

        self.assertEvalError(
            u"(get-index (quote (1)))", wrong_argument_number)

        self.assertEvalError(
            u"(get-index (quote (1)) 0 0)", wrong_argument_number)


class SetIndexTest(BuiltInTestCase):
    def test_set_index_list(self):
        expected = List([Integer.fromint(1)])
        
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
        self.assertEvalError(
            u'(set-index! #bytes("a") 0 #null)', wrong_type)
        
        self.assertEvalError(
            u'(set-index! #bytes("a") 0 1.0)', wrong_type)
        
    def test_set_index_string_type_error(self):
        self.assertEvalError(
            u'(set-index! "abc" 0 #null)', wrong_type)
        
    def test_set_index_bytestring_range_error(self):
        self.assertEvalError(
            u'(set-index! #bytes("a") 0 -1)', value_error)
        
        self.assertEvalError(
            u'(set-index! #bytes("a") 0 256)', value_error)
        
    def test_set_index_negative(self):
        expected = List([Integer.fromint(10), Integer.fromint(1)])
        
        self.assertEqual(
            self.eval(u"(set-symbol! (quote x) (quote (10 20))) (set-index! x -1 1) x"),
            expected)

    def test_set_index_returns_null(self):
        self.assertEqual(
            self.eval(u"(set-index! (quote (2)) 0 1)"),
            NULL)

    def test_set_index_typeerror(self):
        self.assertEvalError(
            u"(set-index! #null 0 0)", wrong_type)

        self.assertEvalError(
            u"(set-index! (quote (1)) #false #false)", wrong_type)

    def test_set_index_indexerror(self):
        self.assertEvalError(
            u"(set-index! (quote ()) 0 #true)", value_error)

        self.assertEvalError(
            u"(set-index! (quote (1)) 2 #true)", value_error)

        self.assertEvalError(
            u"(set-index! (quote (1 2 3)) -4 #true)", value_error)

    def test_set_index_wrong_arg_number(self):
        self.assertEvalError(
            u"(set-index!)", wrong_argument_number)

        self.assertEvalError(
            u"(set-index! (quote (1)))", wrong_argument_number)

        self.assertEvalError(
            u"(set-index! (quote (1)) 0)", wrong_argument_number)

        self.assertEvalError(
            u"(set-index! (quote (1)) 0 5 6)", wrong_argument_number)


class InsertTest(BuiltInTestCase):
    def test_insert(self):
        expected = List([Integer.fromint(1), Integer.fromint(2)])
        
        self.assertEqual(
            self.eval(u"(set-symbol! (quote x) (quote (1))) (insert! x 1 2) x"),
            expected)

    def test_insert_negative(self):
        expected = List([Integer.fromint(1), Integer.fromint(5), Integer.fromint(2)])
        
        self.assertEqual(
            self.eval(u"(set-symbol! (quote x) (quote (1 2))) (insert! x -1 5) x"),
            expected)

    def test_insert_bytestring(self):
        self.assertEqual(
            self.eval(u'(set-symbol! (quote x) #bytes("a")) (insert! x 1 98) x'),
            Bytestring([ord(c) for c in "ab"]))

    def test_insert_bytestring_invalid_type(self):
        self.assertEvalError(
            u'(set-symbol! (quote x) #bytes("a")) (insert! x 1 #null)',
            wrong_type)

    def test_insert_bytestring_invalid_value(self):
        self.assertEvalError(
            u'(set-symbol! (quote x) #bytes("a")) (insert! x 1 256)', value_error)

    def test_insert_string(self):
        self.assertEqual(
            self.eval(u'(set-symbol! (quote x) "a") (insert! x 1 \'b\') x'),
            String(list(u"ab")))

    def test_insert_string_invalid_type(self):
        self.assertEvalError(
            u'(set-symbol! (quote x) "a") (insert! x 1 #null)',
            wrong_type)

    def test_insert_returns_null(self):
        self.assertEqual(
            self.eval(u"(insert! (quote ()) 0 1)"),
            NULL)

    def test_insert_arg_number(self):
        self.assertEvalError(
            u"(insert! (quote ()) 0)", wrong_argument_number)

        self.assertEvalError(
            u"(insert! (quote ()) 0 1 2)", wrong_argument_number)

    def test_insert_indexerror(self):
        self.assertEvalError(
            u"(insert! (quote ()) 1 #null)", value_error)

        self.assertEvalError(
            u"(insert! (quote (1 2)) -3 0)", value_error)

    def test_insert_typeerror(self):
        # first argument must be a sequence
        self.assertEvalError(
            u"(insert! #null 0 0)", wrong_type)

        # second argument must be an integer
        self.assertEvalError(
            u"(insert! (quote ()) 0.0 0)", wrong_type)


class GetKeyTest(BuiltInTestCase):
    def test_get_key_present(self):
        self.assertEqual(
            self.eval(u"(get-key {1 2} 1)"),
            Integer.fromint(2))

    def test_get_key_missing(self):
        self.assertEvalError(
            u"(get-key {1 2} 0)", missing_key)

    def test_get_key_wrong_type(self):
        self.assertEvalError(
            u'(get-key #null 0)', wrong_type)

    def test_get_key_arity(self):
        self.assertEvalError(
            u'(get-key {})', wrong_argument_number)

        self.assertEvalError(
            u'(get-key {} 0 0)', wrong_argument_number)


class SetKeyTest(BuiltInTestCase):
    def test_set_key(self):
        expected = Hashmap()
        expected.dict[Integer.fromint(1)] = Integer.fromint(3)
        
        self.assertEqual(
            self.eval(u"(set-symbol! (quote x) {1 2}) (set-key! x 1 3) x"), expected)

    def test_set_key_returns_null(self):
        self.assertEqual(
            self.eval(u"(set-key! {} 1 3)"), NULL)

    def test_set_key_wrong_type(self):
        self.assertEvalError(
            u'(set-key! #null 0 1)', wrong_type)

    def test_set_key_unhashable_type(self):
        self.assertEvalError(
            u'(set-key! {} "foo" 1)', wrong_type)

    def test_set_key_arity(self):
        self.assertEvalError(
            u'(set-key! {} 0)', wrong_argument_number)

        self.assertEvalError(
            u'(set-key! {} 0 0 0)', wrong_argument_number)


class GetItemsTest(BuiltInTestCase):
    def test_get_items(self):
        expected = self.eval(u"(quote ((1 2)))")
        
        self.assertEqual(
            self.eval(u"(get-items {1 2})"), expected)

    def test_get_items_wrong_type(self):
        self.assertEvalError(
            u'(get-items #null)', wrong_type)

    def test_get_items_arity(self):
        self.assertEvalError(
            u'(get-items)', wrong_argument_number)

        self.assertEvalError(
            u'(get-items {} 0)', wrong_argument_number)


class EnvironmentVariablesTest(BuiltInTestCase):
    def test_evaluate_variable(self):
        env = Environment([Scope({
            u'x': Integer.fromint(1),
        })])
        self.assertEqual(evaluate(parse_one(lex(u"x")), env),
                         Integer.fromint(1))

    def test_unbound_variable(self):
        self.assertEvalError(
            u"x", no_such_variable)


class ParseTest(BuiltInTestCase):
    def test_parse(self):
        expected = parse(lex(u"(+ 1 2)"))

        self.assertEqual(
            self.eval(u"(parse \"(+ 1 2)\")"),
            expected)

    def test_parse_invalid_parse(self):
        self.assertEvalError(
            u'(parse ")")', parse_failed)

        self.assertEvalError(
            u'(parse "(")', parse_failed)

    def test_parse_invalid_lex(self):
        self.assertEvalError(
            u'(parse "123abc")', lex_failed)

    def test_parse_arg_number(self):
        self.assertEvalError(
            u"(parse)", wrong_argument_number)

        self.assertEvalError(
            u'(parse "()" 1)', wrong_argument_number)

    def test_parse_type_error(self):
        self.assertEvalError(
            u"(parse 123)", wrong_type)

    def test_parse_zero_division_error(self):
        self.assertEvalError(
            u'(parse "1/0")', division_by_zero)


class CallTest(BuiltInTestCase):
    def test_call_builtin_function(self):
        self.assertEqual(
            self.eval(u"(call + (quote (1 2 3)))"),
            Integer.fromint(6)
        )

    def test_call_function_with_env(self):
        self.assertEqual(
            self.eval(u"(call defined? (quote (x)))"),
            FALSE
        )

    def test_call_lambda_literal(self):
        self.assertEqual(
            self.eval(u"(call (lambda (x) x) (quote (1)))"),
            Integer.fromint(1)
        )

    def test_call_evals_once(self):
        """Ensure that `call` does not evaluate its arguments more than once.

        """
        self.assertEqual(
            self.eval(u"(call (lambda (x) x) (quote (y)))"),
            Symbol(u'y')
        )

    def test_call_arg_number(self):
        self.assertEvalError(
            u"(call + (quote (1 2 3)) 1)", wrong_argument_number)

        self.assertEvalError(
            u"(call +)", wrong_argument_number)

    def test_call_type(self):
        self.assertEvalError(
            u"(call #null (quote (1 2 3)))", wrong_type)

        self.assertEvalError(
            u"(call + #null)", wrong_type)


class EvalTest(BuiltInTestCase):
    def test_eval(self):
        self.assertEqual(
            self.eval(u"(eval (quote (+ 1 2 3)))"),
            Integer.fromint(6)
        )

    def test_eval_modifies_scope(self):
        self.assertEqual(
            self.eval(u'(set-symbol! (quote x) 0) (eval (quote (set-symbol! (quote x) 1))) x'),
            Integer.fromint(1)
        )


class EvaluatingMacrosTest(BuiltInTestCase):
    def test_macro(self):
        self.assertEqual(
            self.eval(u"(macro just-x (ignored-arg) (quote x)) (set-symbol! (quote x) 1) (just-x y)"),
            Integer.fromint(1)
        )

    def test_call_macro_too_few_args(self):
        self.assertEvalError(
            u"(macro ignore (x) #null) (ignore 1 2)", wrong_argument_number)

    def test_call_macro_too_many_args(self):
        self.assertEvalError(
            u"(macro ignore (x) #null) (ignore)", wrong_argument_number)

    def test_macro_rest_args(self):
        self.assertEqual(
            self.eval(
                u"(macro when (condition :rest body) "
                u"  (quote "
                u"    (if (unquote condition) ((lambda () (unquote* body))) #null)"
                u"  )"
                u")"
                u"(set-symbol! (quote x) 1)"
                u"(when #true (set-symbol! (quote x) 2)) x"),
            Integer.fromint(2)
        )

    def test_macro_bad_args_number(self):
        self.assertEvalError(
            u"(macro foo)", wrong_argument_number)

        self.assertEvalError(
            u"(macro foo (bar))", wrong_argument_number)

    def test_macro_bad_arg_types(self):
        self.assertEvalError(
            u"(macro foo bar #null)", wrong_type)

        self.assertEvalError(
            u"(macro foo (1) #null)", wrong_type)

    def test_macro_bad_name(self):
        self.assertEvalError(
            u"(macro 123 (bar) #null)", wrong_type)

    def test_macro_throw_error(self):
        self.assertEvalError(
            u'(macro foo () (throw error "")) (foo)', error)


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
        self.assertEvalError(
            u"(defined? 1)", wrong_type)

    def test_defined_arity_error(self):
        self.assertEvalError(
            u"(defined?)", wrong_argument_number)
            
        self.assertEvalError(
            u"(defined? (quote foo) 1)", wrong_argument_number)


# TODO: error on nonexistent file, or file we can't read/write
# TODO: support read and write flags together
# TODO: add a seek! function
class OpenTest(BuiltInTestCase):
    def test_open_read(self):
        result = self.eval(u'(open "/etc/hosts" :read)')

        self.assertTrue(isinstance(result, FileHandle))

    def test_open_read_no_such_file(self):
        self.assertEvalError(
            u'(open "this_file_doesnt_exist" :read)', file_not_found)

    def test_open_write(self):
        result = self.eval(u'(open "/tmp/foo" :write)')

        self.assertTrue(isinstance(result, FileHandle))

    def test_open_invalid_flag(self):
        self.assertEvalError(
            u'(open "/tmp/foo" :foo)', value_error)

    def test_open_arity_error(self):
        self.assertEvalError(
            u'(open "/foo/bar")', wrong_argument_number)

        self.assertEvalError(
            u'(open "/foo/bar" :write :write)', wrong_argument_number)

    def test_open_type_error(self):
        self.assertEvalError(
            u'(open "/foo/bar" #null)', wrong_type)

        self.assertEvalError(
            u"(open #null :write)", wrong_type)


class CloseTest(BuiltInTestCase):
    def test_close(self):
        result = self.eval(u'(set-symbol! (quote x) (open "/tmp/foo" :write)) (close! x) x')

        self.assertTrue(result.file_handle.closed)

    def test_close_twice_error(self):
        self.assertEvalError(
            u'(set-symbol! (quote x) (open "/tmp/foo" :write)) (close! x) (close! x)',
            changing_closed_handle)

    def test_close_returns_null(self):
        result = self.eval(u'(close! (open "/tmp/foo" :write))')

        self.assertEqual(result, NULL)

    def test_close_arity_error(self):
        self.assertEvalError(
            u'(close! (open "/tmp/foo" :write) #null)', wrong_argument_number)

        self.assertEvalError(
            u'(close!)', wrong_argument_number)

    def test_close_type_error(self):
        self.assertEvalError(
            u'(close! #null)', wrong_type)


class ReadTest(BuiltInTestCase):
    def test_read(self):
        os.system('echo -n foo > test.txt')
        
        result = self.eval(u'(read (open "test.txt" :read))')

        os.remove('test.txt')

        self.assertEqual(
            result,
            Bytestring([ord(c) for c in "foo"]))

    def test_read_arity(self):
        self.assertEvalError(
            u"(read)", wrong_argument_number)
            
        self.assertEvalError(
            u'(read "/etc/foo" :read :read)', wrong_argument_number)
            
    def test_read_type_error(self):
        self.assertEvalError(
            u"(read #null)", wrong_type)


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
        self.assertEvalError(
            u'(set-symbol! (quote f) (open "/etc/passwd" :read))'
            u'(write! f (encode "foo"))', value_error)

    def test_write_closed_handle(self):
        self.assertEvalError(
            u'(set-symbol! (quote f) (open "foo.txt" :write))'
            u'(close! f)'
            u'(write! f (encode "foo"))',
            changing_closed_handle)

    def test_write_arity(self):
        # Too few args.
        self.assertEvalError(
            u'(write! (open "foo.txt" :write))', wrong_argument_number)

        # Too many args.
        self.assertEvalError(
            u'(write! (open "foo.txt" :write) (encode "f") #null)', wrong_argument_number)
            
    def test_write_type_error(self):
        self.assertEvalError(
            u'(write! #null (encode "f"))', wrong_type)

        self.assertEvalError(
            u'(write! (open "foo.txt" :write) #null)', wrong_type)

        os.remove('foo.txt')


class FlushTest(BuiltInTestCase):
    def test_flush(self):
        # TODO: find some more useful things to assert.
        self.assertEqual(
            self.eval(
                u'(set-symbol! (quote f) (open "test.txt" :write))'
                u'(flush! f)'),
            NULL)

    def test_can_flush_repeatedly(self):
        # Regression test.
        self.assertEqual(
            self.eval(
                u'(set-symbol! (quote f) (open "test.txt" :write))'
                u'(flush! f) (flush! f)'),
            NULL)

    def test_can_flush_stdout(self):
        # Regression test.
        self.assertEqual(
            self.eval(
                u'(flush! stdout)'),
            NULL)

    def test_write_closed_handle(self):
        self.assertEvalError(
            u'(set-symbol! (quote f) (open "foo.txt" :write))'
            u'(close! f) (flush! f)',
            changing_closed_handle)

    def test_write_arity(self):
        # Too few args.
        self.assertEvalError(
            u'(flush!)', wrong_argument_number)

        # Too many args.
        self.assertEvalError(
            u'(flush! (open "foo.txt" :write) #null)',
            wrong_argument_number)
            
    def test_write_type_error(self):
        self.assertEvalError(
            u'(flush! #null)', wrong_type)


class EncodeTest(BuiltInTestCase):
    def test_encode(self):
        self.assertEqual(
            self.eval(u'(encode "soufflé")'),
            Bytestring([ord(c) for c in b"souffl\xc3\xa9"]))
    
    def test_encode_type_error(self):
        self.assertEvalError(
            u'(encode #null)', wrong_type)
    
    def test_encode_arity_error(self):
        self.assertEvalError(
            u'(encode)', wrong_argument_number)
    
        self.assertEvalError(
            u'(encode "foo" 2)', wrong_argument_number)
    

class DecodeTest(BuiltInTestCase):
    def test_decode(self):
        self.assertEqual(
            self.eval(u'(decode #bytes("souffl\\xc3\\xa9"))'),
            String(list(u"soufflé")))

    def test_encode_type_error(self):
        self.assertEvalError(
            u'(decode #null)', wrong_type)
    
    def test_encode_arity_error(self):
        self.assertEvalError(
            u'(decode)', wrong_argument_number)
    
        self.assertEvalError(
            u'(decode #bytes("souffl\\xc3\\xa9") 1)', wrong_argument_number)
    

class SymbolPredicateTest(BuiltInTestCase):
    def test_is_symbol(self):
        self.assertEqual(
            self.eval(u'(symbol? (quote x))'),
            TRUE)

    def test_is_not_symbol(self):
        self.assertEqual(
            self.eval(u'(symbol? #bytes(""))'),
            FALSE)

        self.assertEqual(
            self.eval(u'(symbol? #null)'),
            FALSE)

        self.assertEqual(
            self.eval(u'(symbol? 1.0)'),
            FALSE)

    def test_is_symbol_arity(self):
        self.assertEvalError(
            u'(symbol?)', wrong_argument_number)

        self.assertEvalError(
            u'(symbol? #null #null)', wrong_argument_number)


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
        self.assertEvalError(
            u'(list?)', wrong_argument_number)

        self.assertEvalError(
            u'(list? #null #null)', wrong_argument_number)


class HashmapPredicateTest(BuiltInTestCase):
    def test_is_hashmap(self):
        self.assertEqual(
            self.eval(u'(hashmap? {})'),
            TRUE)

    def test_is_not_hashmap(self):
        self.assertEqual(
            self.eval(u'(hashmap? #bytes(""))'),
            FALSE)

        self.assertEqual(
            self.eval(u'(hashmap? #null)'),
            FALSE)

        self.assertEqual(
            self.eval(u'(hashmap? 1.0)'),
            FALSE)

    def test_is_hashmap_arity(self):
        self.assertEvalError(
            u'(hashmap?)', wrong_argument_number)

        self.assertEvalError(
            u'(hashmap? #null #null)', wrong_argument_number)


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
        self.assertEvalError(
            u'(string?)', wrong_argument_number)

        self.assertEvalError(
            u'(string? #null #null)', wrong_argument_number)


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
        self.assertEvalError(
            u'(bytestring?)', wrong_argument_number)

        self.assertEvalError(
            u'(bytestring? #null #null)', wrong_argument_number)


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
        self.assertEvalError(
            u'(character?)', wrong_argument_number)

        self.assertEvalError(
            u'(character? #null #null)', wrong_argument_number)


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
            self.eval(u"(try (/ 1 0) :catch division-by-zero e #null)"),
            NULL)

    def test_try_catch_everything(self):
        """`error` should be a base exception that we can catch in the case of
        any exception.

        """
        self.assertEqual(
            self.eval(u"(try (/ 1 0) :catch error e #null)"),
            NULL)

    def test_try_with_matching_error_indirect(self):
        """We should catch the error even if it occurs lower on the stack.

        """
        self.assertEqual(
            self.eval(u"(set-symbol! (quote f) (lambda () (/ 1 0 )))"
                      u"(try (f) :catch division-by-zero e #null)"),
            NULL)

    def test_try_without_matching_error(self):
        """If an error occurs, we should not evaluate the catch block if it
        does not match.

        """
        self.assertEvalError(
            u"(try (/ 1 0) :catch no-such-variable e #null)",
            division_by_zero)

    def test_try_without_error(self):
        """If no error occurs, we should not evaluate the catch block.

        """
        self.assertEqual(
            self.eval(u"(try 1 :catch no-such-variable e #null)"),
            Integer.fromint(1))

    def test_try_arity(self):
        # TODO: support multiple catch statements

        # Too few arguments.
        self.assertEvalError(
            u"(try x :catch division-by-zero e)", wrong_argument_number)

        # Too many arguments.
        self.assertEvalError(
            u"(try x :catch division-by-zero e #null #null)", wrong_argument_number)

    def test_catch_error_propagates(self):
        """If an error occurs during the evaluation of the catch block, it
        should propagate as usual.

        """
        self.assertEvalError(
            u"(try (/ 1 0) :catch division-by-zero e x)", no_such_variable)

    def test_exception_as_normal_value(self):
        """If we save an error in a variable, it shouldn't propagate up the
        stack.

        """
        self.assertEqual(
            self.eval(u"(try (/ 1 0) :catch division-by-zero e (same? e 1))"),
            FALSE)

    def test_catch_error_propagates_same_type(self):
        """If an error occurs during the evaluation of the catch block, it
        should propagate as usual, even if it's the type we were catching.

        """
        self.assertEvalError(
            u"(try (/ 1 0) :catch division-by-zero e (/ 1 0))",
            division_by_zero)

    def test_unknown_exception_throws_first(self):
        """If we reference an unknown variable for our exception type, we
        should always throw an exception. It signifies a bug, and it's
        nice to catch it early.

        """
        self.assertEvalError(
            u"(try (/ 1 0) :catch i-dont-exist e #null)", no_such_variable)

    def test_catch_arity_error(self):
        # Regression tests.
        self.assertEqual(
            self.eval(u"(try (/) :catch error e #null)"),
            NULL)

        self.assertEqual(
            self.eval(u"(try (if) :catch error e #null)"),
            NULL)

    def test_catch_stack_overflow(self):
        # Regression test.
        self.assertEqual(
            self.eval(u"(set-symbol! (quote f) (lambda () (f)))"
                      u"(try (f) :catch error e #null)"),
            NULL)

    def test_try_types(self):
        # Third argument isn't `:catch`
        self.assertEvalError(
            u"(try (/ 1 0) :foo division-by-zero #null 1)",
            wrong_type)
        self.assertEvalError(
            u"(try (/ 1 0) #null division-by-zero e #null)",
            wrong_type)

        # Fourth argument isn't an exception type
        self.assertEvalError(
            u"(try (/ 1 0) :catch #null e 1)",
            wrong_type)

        # Fifth argument isn't a symbol.
        self.assertEvalError(
            u"(try (/ 1 0) :catch division-by-zero #null 1)",
            wrong_type)


class ThrowTest(BuiltInTestCase):
    def test_arity(self):
        self.assertEvalError(
            u'(throw error "foo" #null)',
            wrong_argument_number)
        self.assertEvalError(
            u'(throw error)',
            wrong_argument_number)

    def test_types(self):
        self.assertEvalError(
            u'(throw error #null)',
            wrong_type)
        self.assertEvalError(
            u'(throw #null "foo")',
            wrong_type)

    def test_exception_thrown(self):
        self.assertEvalError(
            u'(throw error "foo")',
            error)


class MessageTest(BuiltInTestCase):
    def test_arity(self):
        self.assertEvalError(
            u'(message)',
            wrong_argument_number)
        
        self.assertEvalError(
            u'(message 1 1)',
            wrong_argument_number)

    def test_type(self):
        self.assertEvalError(
            u'(message #null)',
            wrong_type)

    def test_message(self):
        self.assertEqual(
            self.eval(u'(try (throw error "foo") :catch error e (message e))'),
            String(list(u'foo'))
        )


class PrintableTest(BuiltInTestCase):
    def test_arity(self):
        self.assertEvalError(
            u'(printable)',
            wrong_argument_number)
        
        self.assertEvalError(
            u'(printable 1 1)',
            wrong_argument_number)

    def test_printable(self):
        self.assertEqual(
            self.eval(u'(printable "foo")'),
            String(list(u'"foo"')))


class ExceptionTypeTest(BuiltInTestCase):
    def test_arity(self):
        self.assertEvalError(
            u'(exception-type)',
            wrong_argument_number)
        
        self.assertEvalError(
            u'(exception-type (try x :catch error e e) #null)',
            wrong_argument_number)

    def test_wrong_type(self):
        self.assertEvalError(
            u'(exception-type #null)',
            wrong_type)

    def test_exception_type(self):
        self.assertEqual(
            self.eval(u'(exception-type (try (/ 1 0) :catch error e e))'),
            division_by_zero)
