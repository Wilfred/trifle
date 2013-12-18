import unittest

from lexer import lex
from parser import parse_one, parse
from trifle_types import (List, Integer, Symbol, Keyword, Lambda,
                          TRUE, FALSE, NULL)
from evaluator import (evaluate, evaluate_with_built_ins,
                       evaluate_all_with_built_ins)
from errors import UnboundVariable, TrifleTypeError, LexFailed
from environment import Environment

"""Trifle unit tests. These are intended to be run with CPython, and
no effort has been made to make them RPython friendly.

"""

class CommentLex(unittest.TestCase):
    def test_lex_comment(self):
        self.assertEqual(
            lex("1 ; 2 \n 3"), [Integer(1), Integer(3)])


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

        self.assertEqual(
            lex("foo!")[0], Symbol('foo!'))

        self.assertEqual(
            lex("<=")[0], Symbol('<='))

    def test_lex_invalid_symbol(self):
        with self.assertRaises(LexFailed):
            lex("\\")


class KeywordLex(unittest.TestCase):
    def test_lex_keyword(self):
        self.assertEqual(
            lex(":x")[0], Keyword('x'))

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


class NullLex(unittest.TestCase):
    def test_lex_boolean(self):
        self.assertEqual(
            lex("null")[0], NULL)


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


class EvaluatingLiterals(unittest.TestCase):
    def test_eval_boolean(self):
        self.assertEqual(
            evaluate_with_built_ins(parse_one(lex("true"))),
            TRUE)

        self.assertEqual(
            evaluate_with_built_ins(parse_one(lex("false"))),
            FALSE)

    def test_eval_integer(self):
        self.assertEqual(
            evaluate_with_built_ins(parse_one(lex("123"))),
            Integer(123))

    def test_eval_null(self):
        self.assertEqual(
            evaluate_with_built_ins(parse_one(lex("null"))),
            NULL)

    def test_eval_keyword(self):
        self.assertEqual(
            evaluate_with_built_ins(parse_one(lex(":foo"))),
            Keyword("foo"))


class EvaluatingLambda(unittest.TestCase):
    def test_call_lambda(self):
        self.assertEqual(
            evaluate_with_built_ins(
                parse_one(lex("((lambda (x) x) 1)"))),
            Integer(1))

    def test_call_lambda_variable_arguments(self):
        expected = List()
        expected.values = [Integer(1), Integer(2), Integer(3), Integer(4)]
        
        self.assertEqual(
            evaluate_with_built_ins(
                parse_one(lex("((lambda (:rest args) args) 1 2 3 4)"))),
            expected)

    def test_call_lambda_too_few_variable_arguments(self):
        with self.assertRaises(TrifleTypeError):
            evaluate_with_built_ins(
                parse_one(lex("((lambda (x y :rest args) x))")))

    def test_lambda_wrong_arg_number(self):
        with self.assertRaises(TrifleTypeError):
            evaluate_with_built_ins(
                parse_one(lex("(lambda)")))

    def test_lambda_params_not_list(self):
        with self.assertRaises(TrifleTypeError):
            evaluate_with_built_ins(
                parse_one(lex("(lambda foo bar)")))

    def test_lambda_params_not_symbols(self):
        with self.assertRaises(TrifleTypeError):
            evaluate_with_built_ins(
                parse_one(lex("(lambda (1 2) bar)")))

    def test_evaluate_lambda(self):
        lambda_obj = evaluate_with_built_ins(
            parse_one(lex("(lambda (x) x)")))

        self.assertTrue(isinstance(lambda_obj, Lambda),
                        "Expected a lambda object but got a %s" % lambda_obj.__class__)


    def test_lambda_scope_doesnt_leak(self):
        """Ensure that defining a variable inside a lambda is accessible
        inside the body, but doesn't leak outside.

        """
        self.assertEqual(
            evaluate_with_built_ins(
                parse_one(lex("((lambda () (set! x 2) x))"))),
            Integer(2))

        with self.assertRaises(UnboundVariable):
            evaluate_with_built_ins(
                parse_one(lex("((lambda () (set! x 2)) x)")))

    def test_closure_variables(self):
        """Ensure that we can update closure variables inside a lambda.

        """
        self.assertEqual(
            evaluate_all_with_built_ins(
                parse(lex("(set! x 1) ((lambda () (set! x 2))) x"))),
            Integer(2))


class Do(unittest.TestCase):
    def test_do(self):
        self.assertEqual(
            evaluate_with_built_ins(
                parse_one(lex("(do 1 2)"))),
            Integer(2))

    def test_do_no_args(self):
        self.assertEqual(
            evaluate_with_built_ins(
                parse_one(lex("(do)"))),
            NULL)


class Set(unittest.TestCase):
    def test_set(self):
        self.assertEqual(
            evaluate_all_with_built_ins(
                parse(lex("(set! x 1) x"))),
            Integer(1))

    def test_set_wrong_arg_number(self):
        with self.assertRaises(TrifleTypeError):
            evaluate_with_built_ins(
                parse_one(lex("(set! x 1 2)")))

    def test_set_returns_null(self):
        self.assertEqual(
            evaluate_with_built_ins(
                parse_one(lex("(set! x 1)"))),
            NULL)

# todo: decide whether quote should construct fresh values each time
# i.e. (function foo () (set! x (quote ())) (push! x 1) x)
# what does (do (foo) (foo)) evlauate to?
class Quote(unittest.TestCase):
    def test_quote(self):
        expected = parse_one(lex("(+ 1 2)"))
        
        self.assertEqual(
            evaluate_with_built_ins(parse_one(lex("(quote (+ 1 2))"))),
            expected)

    def test_quote_wrong_number_args(self):
        with self.assertRaises(TrifleTypeError):
            evaluate_with_built_ins(parse_one(lex("(quote foo bar)")))

    def test_unquote(self):
        expected = List()
        expected.append(Symbol('x'))
        expected.append(Integer(1))
        
        self.assertEqual(
            evaluate_all_with_built_ins(parse(lex(
                "(set! x 1) (quote (x (unquote x)))"))),
            expected)

    def test_unquote_star(self):
        expected = List()
        expected.append(Symbol('baz'))
        expected.append(Symbol('foo'))
        expected.append(Symbol('bar'))
        
        self.assertEqual(
            evaluate_all_with_built_ins(parse(lex(
                "(set! x (quote (foo bar))) (quote (baz (unquote* x)))"))),
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


class If(unittest.TestCase):
    def test_if_one_arg(self):
        self.assertEqual(
            evaluate_with_built_ins(parse_one(lex("(if true 1)"))),
            Integer(1))

        self.assertEqual(
            evaluate_with_built_ins(parse_one(lex("(if false 1)"))),
            NULL)

    def test_if_two_args(self):
        self.assertEqual(
            evaluate_with_built_ins(parse_one(lex("(if true 2 3)"))),
            Integer(2))

        self.assertEqual(
            evaluate_with_built_ins(parse_one(lex("(if false 4 5)"))),
            Integer(5))

    def test_if_wrong_number_of_args(self):
        with self.assertRaises(TrifleTypeError):
            evaluate_with_built_ins(
                parse_one(lex("(if)")))

        with self.assertRaises(TrifleTypeError):
            evaluate_with_built_ins(
                parse_one(lex("(if 1 2 3 4)")))


class Truthy(unittest.TestCase):
    def test_truthy(self):
        self.assertEqual(
            evaluate_with_built_ins(parse_one(lex("(truthy? 2)"))),
            TRUE)
        
        self.assertEqual(
            evaluate_with_built_ins(parse_one(lex("(truthy? 0)"))),
            FALSE)
        
        self.assertEqual(
            evaluate_with_built_ins(parse_one(lex("(truthy? false)"))),
            FALSE)
        
        self.assertEqual(
            evaluate_with_built_ins(parse_one(lex("(truthy? true)"))),
            TRUE)
        
        self.assertEqual(
            evaluate_with_built_ins(parse_one(lex("(truthy? (quote ()))"))),
            FALSE)
        
        self.assertEqual(
            evaluate_with_built_ins(parse_one(lex("(truthy? (quote (1)))"))),
            TRUE)

    def test_if_wrong_number_of_args(self):
        with self.assertRaises(TrifleTypeError):
            evaluate_with_built_ins(
                parse_one(lex("(truthy?)")))

        with self.assertRaises(TrifleTypeError):
            evaluate_with_built_ins(
                parse_one(lex("(truthy? 1 2)")))


class While(unittest.TestCase):
    def test_while_false_condition(self):
        # `(while)` is an error, but this should work as while should
        # not evaluate the body here.
        self.assertEqual(
            evaluate_with_built_ins(parse_one(lex("(while false (while))"))),
            NULL)

    def test_while_true_condition(self):
        # `(while)` is an error, but this should work as while should
        # not evaluate the body here.
        self.assertEqual(
            evaluate_all_with_built_ins(parse(lex(
                "(set! x true) (set! y 1) (while x (set! x false) (set! y 2)) y"))),
            Integer(2))
        
    def test_while_wrong_number_of_args(self):
        with self.assertRaises(TrifleTypeError):
            evaluate_with_built_ins(
                parse_one(lex("(while)")))


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

    def test_null_same(self):
        self.assertEqual(
            evaluate_with_built_ins(parse_one(lex("(same? null null)"))),
            TRUE)

    def test_symbol_same(self):
        self.assertEqual(
            evaluate_with_built_ins(parse_one(lex("(same? (quote a) (quote a))"))),
            TRUE)

    def test_list_same(self):
        self.assertEqual(
            evaluate_all_with_built_ins(parse(lex("(set! x (quote ())) (same? x x)"))),
            TRUE)

    def test_function_same(self):
        self.assertEqual(
            evaluate_with_built_ins(parse_one(lex("(same? same? same?)"))),
            TRUE)

    def test_lambda_same(self):
        self.assertEqual(
            evaluate_all_with_built_ins(parse(lex("(set! x (lambda () 1)) (same? x x)"))),
            TRUE)

    def test_special_same(self):
        self.assertEqual(
            evaluate_with_built_ins(parse_one(lex("(same? if if)"))),
            TRUE)

    def test_different_types(self):
        self.assertEqual(
            evaluate_with_built_ins(parse_one(lex("(same? true 1)"))),
            FALSE)

    def test_same_wrong_number_of_args(self):
        with self.assertRaises(TrifleTypeError):
            evaluate_with_built_ins(
                parse_one(lex("(same? 1)")))

        with self.assertRaises(TrifleTypeError):
            evaluate_with_built_ins(
                parse_one(lex("(same? 1 2 3)")))

class LessThan(unittest.TestCase):
    def test_less_than(self):
        self.assertEqual(
            evaluate_with_built_ins(parse_one(lex("(< 1 2)"))),
            TRUE)

        self.assertEqual(
            evaluate_with_built_ins(parse_one(lex("(< 3 2)"))),
            FALSE)

    def test_less_than_typeerror(self):
        with self.assertRaises(TrifleTypeError):
            evaluate_with_built_ins(parse_one(lex("(< true false)")))

    def test_less_than_insufficient_args(self):
        with self.assertRaises(TrifleTypeError):
            evaluate_with_built_ins(parse_one(lex("(<)")))

        with self.assertRaises(TrifleTypeError):
            evaluate_with_built_ins(parse_one(lex("(< 1)")))


class EnvironmentVariables(unittest.TestCase):
    def test_evaluate_variable(self):
        env = Environment([{
            'x': Integer(1),
        }])
        self.assertEqual(evaluate(parse_one(lex("x")), env),
                         Integer(1))

    def test_unbound_variable(self):
        with self.assertRaises(UnboundVariable):
            evaluate_with_built_ins(parse_one(lex("x")))


class EvaluatingMacros(unittest.TestCase):
    def test_macro(self):
        self.assertEqual(
            evaluate_all_with_built_ins(parse(lex(
                "(macro just-x (ignored-arg) (quote x)) (set! x 1) (just-x y)"))),
            Integer(1)
        )

    def test_macro_bad_args(self):
        with self.assertRaises(TrifleTypeError):
            evaluate_with_built_ins(parse_one(lex(
                "(macro foo)")))

        with self.assertRaises(TrifleTypeError):
            evaluate_with_built_ins(parse_one(lex(
                "(macro foo bar)")))

        with self.assertRaises(TrifleTypeError):
            evaluate_with_built_ins(parse_one(lex(
                "(macro foo (1))")))

        with self.assertRaises(TrifleTypeError):
            evaluate_with_built_ins(parse_one(lex(
                "(macro 123 (bar))")))


if __name__ == '__main__':
    unittest.main()
