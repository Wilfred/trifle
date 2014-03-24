import unittest

from trifle_types import (List, Bytestring, String, Character,
                          Integer,
                          TRUE, FALSE, NULL)
from main import env_with_prelude
from evaluator import evaluate, evaluate_all
from trifle_parser import parse_one, parse
from lexer import lex
from errors import TrifleValueError, TrifleTypeError, ArityError


"""Unit tests for functions and macros in the prelude. It's easier to
test in Python than in Trifle, since Trifle code uses many parts of
the prelude very often.

"""

# TODO: we should shell out to the RPython-compiled binary instead of
# assuming CPython behaves the same.

# TODO: factor out evaluating with fresh env

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


class ZeroPredicateTest(unittest.TestCase):
    def test_not_zero(self):
        self.assertEqual(
            evaluate(parse_one(lex(u"(zero? 5)")), env_with_prelude()),
            FALSE)

        self.assertEqual(
            evaluate(parse_one(lex(u"(zero? -3)")), env_with_prelude()),
            FALSE)

        self.assertEqual(
            evaluate(parse_one(lex(u"(zero? #null)")), env_with_prelude()),
            FALSE)

    def test_zero(self):
        self.assertEqual(
            evaluate(parse_one(lex(u"(zero? 0)")), env_with_prelude()),
            TRUE)

        self.assertEqual(
            evaluate(parse_one(lex(u"(zero? 0.0)")), env_with_prelude()),
            TRUE)

        self.assertEqual(
            evaluate(parse_one(lex(u"(zero? -0.0)")), env_with_prelude()),
            TRUE)


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

    def test_map_bytestring(self):
        self.assertEqual(
            evaluate(parse_one(lex(u'(map (lambda (x) (+ x 1)) #bytes("abc"))')),
                     env_with_prelude()),
            Bytestring([ord(c) for c in "bcd"]))

    def test_map_string(self):
        self.assertEqual(
            evaluate(parse_one(lex(u'(map (lambda (x) \'z\') "abc")')),
                     env_with_prelude()),
            String(list(u"zzz")))


class NthItemTest(unittest.TestCase):
    def test_first(self):
        self.assertEqual(
            evaluate(parse_one(lex(u"(first (list 1 2 3 4 5))")),
                     env_with_prelude()),
            Integer(1))
        
    def test_first_bytestring(self):
        self.assertEqual(
            evaluate(parse_one(lex(u'(first #bytes("abc"))')),
                     env_with_prelude()),
            Integer(97))
        
    def test_first_string(self):
        self.assertEqual(
            evaluate(parse_one(lex(u'(first "abc")')),
                     env_with_prelude()),
            Character(u'a'))
        
    def test_second(self):
        self.assertEqual(
            evaluate(parse_one(lex(u"(second (list 1 2 3 4 5))")),
                     env_with_prelude()),
            Integer(2))
        
    def test_second_bytestring(self):
        self.assertEqual(
            evaluate(parse_one(lex(u'(second #bytes("abc"))')),
                     env_with_prelude()),
            Integer(98))
        
    def test_second_string(self):
        self.assertEqual(
            evaluate(parse_one(lex(u'(second "abc")')),
                     env_with_prelude()),
            Character(u'b'))
        
    def test_third(self):
        self.assertEqual(
            evaluate(parse_one(lex(u"(third (list 1 2 3 4 5))")),
                     env_with_prelude()),
            Integer(3))
        
    def test_third_bytestring(self):
        self.assertEqual(
            evaluate(parse_one(lex(u'(third #bytes("abc"))')),
                     env_with_prelude()),
            Integer(99))
        
    def test_third_string(self):
        self.assertEqual(
            evaluate(parse_one(lex(u'(third "abc")')),
                     env_with_prelude()),
            Character(u'c'))
        
    def test_fourth(self):
        self.assertEqual(
            evaluate(parse_one(lex(u"(fourth (list 1 2 3 4 5))")),
                     env_with_prelude()),
            Integer(4))
        
    def test_fourth_bytestring(self):
        self.assertEqual(
            evaluate(parse_one(lex(u'(fourth #bytes("abcd"))')),
                     env_with_prelude()),
            Integer(100))
        
    def test_fourth_string(self):
        self.assertEqual(
            evaluate(parse_one(lex(u'(fourth "abcd")')),
                     env_with_prelude()),
            Character(u'd'))
        
    def test_fifth(self):
        self.assertEqual(
            evaluate(parse_one(lex(u"(fifth (list 1 2 3 4 5))")),
                     env_with_prelude()),
            Integer(5))

    def test_fifth_bytestring(self):
        self.assertEqual(
            evaluate(parse_one(lex(u'(fifth #bytes("abcde"))')),
                     env_with_prelude()),
            Integer(101))
        
    def test_fifth_string(self):
        self.assertEqual(
            evaluate(parse_one(lex(u'(fifth "abcde")')),
                     env_with_prelude()),
            Character(u'e'))
        

class LastTest(unittest.TestCase):
    def test_last(self):
        self.assertEqual(
            evaluate(parse_one(lex(u"(last (list 1 2 3 4 5))")),
                     env_with_prelude()),
            Integer(5))

    def test_last_bytestring(self):
        self.assertEqual(
            evaluate(parse_one(lex(u'(last #bytes("abc"))')),
                     env_with_prelude()),
            Integer(99))

    def test_last_string(self):
        self.assertEqual(
            evaluate(parse_one(lex(u'(last "abc")')),
                     env_with_prelude()),
            Character(u'c'))

    def test_last_empty_list(self):
        # todo: we need a separate index error
        with self.assertRaises(TrifleValueError):
            evaluate(parse_one(lex(u"(last (list))")),
                     env_with_prelude())


class AppendTest(unittest.TestCase):
    def test_append(self):
        expected = List([Integer(1), Integer(2)])
        
        self.assertEqual(
            evaluate_all(parse(lex(
                u"(set-symbol! (quote x) (quote (1))) (append! x 2) x")),
                         env_with_prelude()),
            expected)

    def test_append_bytestring(self):
        self.assertEqual(
            evaluate_all(parse(lex(
                u'(set-symbol! (quote x) #bytes("a")) (append! x 98) x')),
                         env_with_prelude()),
            Bytestring([ord(c) for c in "ab"]))

    def test_append_string(self):
        self.assertEqual(
            evaluate_all(parse(lex(
                u'(set-symbol! (quote x) "a") (append! x \'b\') x')),
                         env_with_prelude()),
            String(list(u"ab")))

    def test_append_returns_null(self):
        self.assertEqual(
            evaluate(parse_one(lex(
                u"(append! (quote ()) 1)")),
                     env_with_prelude()),
            NULL)

    def test_append_arg_number(self):
        with self.assertRaises(ArityError):
            evaluate(parse_one(lex(
                u"(append! (quote ()))")),
                     env_with_prelude())

        with self.assertRaises(ArityError):
            evaluate(parse_one(lex(
                u"(append! (quote ()) 0 1)")),
                     env_with_prelude())

    def test_append_typeerror(self):
        # first argument must be a list
        with self.assertRaises(TrifleTypeError):
            evaluate(parse_one(lex(
                u"(append! #null 0)")),
                     env_with_prelude())


class PushTest(unittest.TestCase):
    def test_push_list(self):
        expected = List([Integer(1)])
        
        self.assertEqual(
            evaluate_all(parse(lex(
                u"(set-symbol! (quote x) (quote ())) (push! x 1) x")),
                         env_with_prelude()),
            expected)

    def test_push_bytestring(self):
        self.assertEqual(
            evaluate_all(parse(lex(
                u'(set-symbol! (quote x) #bytes("bc")) (push! x 97) x')),
                         env_with_prelude()),
            Bytestring([ord(c) for c in b"abc"]))

    def test_push_string(self):
        self.assertEqual(
            evaluate_all(parse(lex(
                u'(set-symbol! (quote x) "bc") (push! x \'a\') x')),
                         env_with_prelude()),
            String(list(u"abc")))

    def test_push_returns_null(self):
        self.assertEqual(
            evaluate(parse_one(lex(
                u"(push! (quote ()) 1)")),
                     env_with_prelude()),
            NULL)

    def test_push_arg_number(self):
        with self.assertRaises(ArityError):
            evaluate(parse_one(lex(
                u"(push! (quote ()))")),
                     env_with_prelude())

        with self.assertRaises(ArityError):
            evaluate(parse_one(lex(
                u"(push! (quote ()) 0 1)")),
                     env_with_prelude())

    def test_push_typeerror(self):
        # first argument must be a list
        with self.assertRaises(TrifleTypeError):
            evaluate(parse_one(lex(
                u"(push! #null 0)")),
                     env_with_prelude())


class NotTest(unittest.TestCase):
    def test_not_booleans(self):
        self.assertEqual(
            evaluate(parse_one(lex(u"(not #true)")),
                     env_with_prelude()),
            FALSE)
        
        self.assertEqual(
            evaluate(parse_one(lex(u"(not #false)")),
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


class AndTest(unittest.TestCase):
    def test_and(self):
        self.assertEqual(
            evaluate(parse_one(lex(u"(and #true #true)")),
                     env_with_prelude()),
            TRUE)
        self.assertEqual(
            evaluate(parse_one(lex(u"(and #true #false)")),
                     env_with_prelude()),
            FALSE)
        self.assertEqual(
            evaluate(parse_one(lex(u"(and #false #true)")),
                     env_with_prelude()),
            FALSE)
        self.assertEqual(
            evaluate(parse_one(lex(u"(and #false #false)")),
                     env_with_prelude()),
            FALSE)
        
    def test_and_arity(self):
        self.assertEqual(
            evaluate(parse_one(lex(u"(and)")),
                     env_with_prelude()),
            TRUE)

        self.assertEqual(
            evaluate(parse_one(lex(u"(and #true #true #true)")),
                     env_with_prelude()),
            TRUE)

    def test_and_evaluation(self):
        """Statements should not be evaluated more than once."""
        self.assertEqual(
            evaluate_all(parse(lex(
                u"(set! x 0)"
                u"(and (do (inc! x) #true))"
                u"x")),
                     env_with_prelude()),
            Integer(1))


class OrTest(unittest.TestCase):
    def test_or(self):
        self.assertEqual(
            evaluate(parse_one(lex(u"(or #true #true)")),
                     env_with_prelude()),
            TRUE)
        self.assertEqual(
            evaluate(parse_one(lex(u"(or #true #false)")),
                     env_with_prelude()),
            TRUE)
        self.assertEqual(
            evaluate(parse_one(lex(u"(or #false #true)")),
                     env_with_prelude()),
            TRUE)
        self.assertEqual(
            evaluate(parse_one(lex(u"(or #false #false)")),
                     env_with_prelude()),
            FALSE)
        
    def test_or_arity(self):
        self.assertEqual(
            evaluate(parse_one(lex(u"(or)")),
                     env_with_prelude()),
            FALSE)

        self.assertEqual(
            evaluate(parse_one(lex(u"(or #true #true #true)")),
                     env_with_prelude()),
            TRUE)

    def test_or_evaluation(self):
        """Statements should not be evaluated more than once."""
        self.assertEqual(
            evaluate_all(parse(lex(
                u"(set! x 0)"
                u"(or (do (inc! x) #true))"
                u"x")),
                     env_with_prelude()),
            Integer(1))


class RestTest(unittest.TestCase):
    def test_rest(self):
        self.assertEqual(
            evaluate(parse_one(lex(u"(rest (list 1 2 3))")),
                     env_with_prelude()),
            List([Integer(2), Integer(3)]))
        
    def test_rest_bytestring(self):
        self.assertEqual(
            evaluate(parse_one(lex(u'(rest #bytes("abc"))')),
                     env_with_prelude()),
            Bytestring([ord(c) for c in b"bc"]))
        
    def test_rest_string(self):
        self.assertEqual(
            evaluate(parse_one(lex(u'(rest "abc")')),
                     env_with_prelude()),
            String(list(u"bc")))
        
    def test_rest_empty_list(self):
        self.assertEqual(
            evaluate(parse_one(lex(u"(rest (list))")),
                     env_with_prelude()),
            List())
        
        
class UnlessTest(unittest.TestCase):
    def test_unless_true(self):
        self.assertEqual(
            evaluate(parse_one(lex(u"(unless #true 1)")),
                     env_with_prelude()),
            NULL)
        
    def test_unless_false(self):
        self.assertEqual(
            evaluate(parse_one(lex(u"(unless #false 1 2)")),
                     env_with_prelude()),
            Integer(2))
        
class CaseTest(unittest.TestCase):
    def test_case_true(self):
        self.assertEqual(
            evaluate(parse_one(lex(u"(case (#true 1))")),
                     env_with_prelude()),
            Integer(1))

    def test_case_first_match(self):
        self.assertEqual(
            evaluate(parse_one(lex(u"(case (#true 1) (#true 2))")),
                     env_with_prelude()),
            Integer(1))

    def test_case_second_match(self):
        self.assertEqual(
            evaluate(parse_one(lex(u"(case (#false 1) (#true 2))")),
                     env_with_prelude()),
            Integer(2))

    def test_clause_body_in_correct_scope(self):
        self.assertEqual(
            evaluate(parse_one(lex(u"(let (x 2) (case (#false 1) (#true x)))")),
                     env_with_prelude()),
            Integer(2))


class TruthyTest(unittest.TestCase):
    def test_truthy_integers(self):
        self.assertEqual(
            evaluate(parse_one(lex(u"(truthy? 2)")), env_with_prelude()),
            TRUE)
        
        self.assertEqual(
            evaluate(parse_one(lex(u"(truthy? 0)")), env_with_prelude()),
            FALSE)

    def test_truthy_floats(self):
        self.assertEqual(
            evaluate(parse_one(lex(u"(truthy? -0.2)")), env_with_prelude()),
            TRUE)
        
        self.assertEqual(
            evaluate(parse_one(lex(u"(truthy? 0.0)")), env_with_prelude()),
            FALSE)

    def test_truthy_bools(self):
        self.assertEqual(
            evaluate(parse_one(lex(u"(truthy? #false)")), env_with_prelude()),
            FALSE)
        
        self.assertEqual(
            evaluate(parse_one(lex(u'(truthy? "foo")')), env_with_prelude()),
            TRUE)

    def test_truthy_strings(self):
        self.assertEqual(
            evaluate(parse_one(lex(u'(truthy? "")')), env_with_prelude()),
            FALSE)
        
        self.assertEqual(
            evaluate(parse_one(lex(u'(truthy? "foo")')), env_with_prelude()),
            TRUE)

    def test_truthy_bytestrings(self):
        self.assertEqual(
            evaluate(parse_one(lex(u'(truthy? #bytes(""))')), env_with_prelude()),
            FALSE)
        
        self.assertEqual(
            evaluate(parse_one(lex(u'(truthy? #bytes("foo"))')), env_with_prelude()),
            TRUE)

    def test_truthy_lists(self):
        self.assertEqual(
            evaluate(parse_one(lex(u"(truthy? (list))")), env_with_prelude()),
            FALSE)
        
        self.assertEqual(
            evaluate(parse_one(lex(u"(truthy? (list (list)))")), env_with_prelude()),
            TRUE)

    def test_truthy_wrong_number_of_args(self):
        with self.assertRaises(ArityError):
            evaluate(parse_one(lex(u"(truthy?)")), env_with_prelude())

        with self.assertRaises(ArityError):
            evaluate(parse_one(lex(u"(truthy? 1 2)")), env_with_prelude())


class RangeTest(unittest.TestCase):
    def test_range(self):
        self.assertEqual(
            evaluate(parse_one(lex(u"(range 5)")), env_with_prelude()),
            evaluate(parse_one(lex(u"(list 0 1 2 3 4)")), env_with_prelude())
        )
