import unittest

from trifle_types import (List, Bytestring, String, Character,
                          Integer,
                          TRUE, FALSE, NULL)
from trifle_parser import parse_one, parse
from lexer import lex
from errors import TrifleValueError, TrifleTypeError, ArityError

from test_utils import (
    evaluate_with_prelude, evaluate_all_with_prelude
)


"""Unit tests for functions and macros in the prelude. It's easier to
test in Python than in Trifle, since Trifle code uses many parts of
the prelude very often.

"""

# TODO: we should shell out to the RPython-compiled binary instead of
# assuming CPython behaves the same.

class SetTest(unittest.TestCase):
    def test_set(self):
        self.assertEqual(
            evaluate_all_with_prelude(
                parse(lex(u"(set! x 1) x"))),
            Integer(1))

    def test_set_returns_null(self):
        self.assertEqual(
            evaluate_with_prelude(
                parse_one(lex(u"(set! x 1)"))),
            NULL)


class DoTest(unittest.TestCase):
    def test_do(self):
        self.assertEqual(
            evaluate_with_prelude(parse_one(lex(u"(do 1 2)"))),
            Integer(2))

    def test_do_no_args(self):
        self.assertEqual(
            evaluate_with_prelude(parse_one(lex(u"(do)"))),
            NULL)


class IdentityTest(unittest.TestCase):
    def test_identity(self):
        self.assertEqual(
            evaluate_with_prelude(parse_one(lex(u"(identity 123)"))),
            Integer(123))


class IncTest(unittest.TestCase):
    def test_inc(self):
        self.assertEqual(
            evaluate_with_prelude(parse_one(lex(u"(inc 5)"))),
            Integer(6))

    def test_inc_macro(self):
        self.assertEqual(
            evaluate_all_with_prelude(parse(lex(u"(set! x 2) (inc! x) x"))),
            Integer(3))


class ZeroPredicateTest(unittest.TestCase):
    def test_not_zero(self):
        self.assertEqual(
            evaluate_with_prelude(parse_one(lex(u"(zero? 5)"))),
            FALSE)

        self.assertEqual(
            evaluate_with_prelude(parse_one(lex(u"(zero? -3)"))),
            FALSE)

        self.assertEqual(
            evaluate_with_prelude(parse_one(lex(u"(zero? #null)"))),
            FALSE)

    def test_zero(self):
        self.assertEqual(
            evaluate_with_prelude(parse_one(lex(u"(zero? 0)"))),
            TRUE)

        self.assertEqual(
            evaluate_with_prelude(parse_one(lex(u"(zero? 0.0)"))),
            TRUE)

        self.assertEqual(
            evaluate_with_prelude(parse_one(lex(u"(zero? -0.0)"))),
            TRUE)


class DecTest(unittest.TestCase):
    def test_dec(self):
        self.assertEqual(
            evaluate_with_prelude(parse_one(lex(u"(dec 5)"))),
            Integer(4))

    def test_dec_macro(self):
        self.assertEqual(
            evaluate_all_with_prelude(parse(lex(u"(set! x 2) (dec! x) x"))),
            Integer(1))


class ForEachTest(unittest.TestCase):
    def test_for_each(self):
        self.assertEqual(
            evaluate_with_prelude(parse_one(lex(u"""(let (total 0 numbers (list 1 2 3 4))
            (for-each number numbers (set! total (+ total number)))
            total)"""))),
            Integer(10))


class ListTest(unittest.TestCase):
    def test_list(self):
        expected = List([Integer(1), Integer(2), Integer(3)])

        self.assertEqual(
            evaluate_with_prelude(parse_one(lex(u"(list 1 2 3)"))),
            expected)


class MapTest(unittest.TestCase):
    def test_map(self):
        expected = List([Integer(2), Integer(3), Integer(4)])

        self.assertEqual(
            evaluate_with_prelude(parse_one(lex(u"(map (lambda (x) (+ x 1)) (list 1 2 3))"))),
            expected)

    def test_map_bytestring(self):
        self.assertEqual(
            evaluate_with_prelude(parse_one(lex(u'(map (lambda (x) (+ x 1)) #bytes("abc"))'))),
            Bytestring([ord(c) for c in "bcd"]))

    def test_map_string(self):
        self.assertEqual(
            evaluate_with_prelude(parse_one(lex(u'(map (lambda (x) \'z\') "abc")'))),
            String(list(u"zzz")))


class FilterTest(unittest.TestCase):
    def test_filter(self):
        expected = List([Integer(2)])

        self.assertEqual(
            evaluate_with_prelude(parse_one(lex(u"(filter (lambda (x) (equal? x 2)) (list 1 2 3))"))),
            expected)

    def test_map_bytestring(self):
        self.assertEqual(
            evaluate_with_prelude(parse_one(lex(u'(filter (lambda (x) (equal? x 98)) #bytes("abc"))'))),
            Bytestring([ord("b")]))

    def test_map_string(self):
        self.assertEqual(
            evaluate_with_prelude(parse_one(lex(u'(filter (lambda (x) (equal? x \'b\')) "abc")'))),
            String(list(u"b")))


class NthItemTest(unittest.TestCase):
    def test_first(self):
        self.assertEqual(
            evaluate_with_prelude(parse_one(lex(u"(first (list 1 2 3 4 5))"))),
            Integer(1))
        
    def test_first_bytestring(self):
        self.assertEqual(
            evaluate_with_prelude(parse_one(lex(u'(first #bytes("abc"))'))),
            Integer(97))
        
    def test_first_string(self):
        self.assertEqual(
            evaluate_with_prelude(parse_one(lex(u'(first "abc")'))),
            Character(u'a'))
        
    def test_second(self):
        self.assertEqual(
            evaluate_with_prelude(parse_one(lex(u"(second (list 1 2 3 4 5))"))),
            Integer(2))
        
    def test_second_bytestring(self):
        self.assertEqual(
            evaluate_with_prelude(parse_one(lex(u'(second #bytes("abc"))'))),
            Integer(98))
        
    def test_second_string(self):
        self.assertEqual(
            evaluate_with_prelude(parse_one(lex(u'(second "abc")'))),
            Character(u'b'))
        
    def test_third(self):
        self.assertEqual(
            evaluate_with_prelude(parse_one(lex(u"(third (list 1 2 3 4 5))"))),
            Integer(3))
        
    def test_third_bytestring(self):
        self.assertEqual(
            evaluate_with_prelude(parse_one(lex(u'(third #bytes("abc"))'))),
            Integer(99))
        
    def test_third_string(self):
        self.assertEqual(
            evaluate_with_prelude(parse_one(lex(u'(third "abc")'))),
            Character(u'c'))
        
    def test_fourth(self):
        self.assertEqual(
            evaluate_with_prelude(parse_one(lex(u"(fourth (list 1 2 3 4 5))"))),
            Integer(4))
        
    def test_fourth_bytestring(self):
        self.assertEqual(
            evaluate_with_prelude(parse_one(lex(u'(fourth #bytes("abcd"))'))),
            Integer(100))
        
    def test_fourth_string(self):
        self.assertEqual(
            evaluate_with_prelude(parse_one(lex(u'(fourth "abcd")'))),
            Character(u'd'))
        
    def test_fifth(self):
        self.assertEqual(
            evaluate_with_prelude(parse_one(lex(u"(fifth (list 1 2 3 4 5))"))),
            Integer(5))

    def test_fifth_bytestring(self):
        self.assertEqual(
            evaluate_with_prelude(parse_one(lex(u'(fifth #bytes("abcde"))'))),
            Integer(101))
        
    def test_fifth_string(self):
        self.assertEqual(
            evaluate_with_prelude(parse_one(lex(u'(fifth "abcde")'))),
            Character(u'e'))
        

class LastTest(unittest.TestCase):
    def test_last(self):
        self.assertEqual(
            evaluate_with_prelude(parse_one(lex(u"(last (list 1 2 3 4 5))"))),
            Integer(5))

    def test_last_bytestring(self):
        self.assertEqual(
            evaluate_with_prelude(parse_one(lex(u'(last #bytes("abc"))'))),
            Integer(99))

    def test_last_string(self):
        self.assertEqual(
            evaluate_with_prelude(parse_one(lex(u'(last "abc")'))),
            Character(u'c'))

    def test_last_empty_list(self):
        # todo: we need a separate index error
        with self.assertRaises(TrifleValueError):
            evaluate_with_prelude(parse_one(lex(u"(last (list))")))


class AppendTest(unittest.TestCase):
    def test_append(self):
        expected = List([Integer(1), Integer(2)])
        
        self.assertEqual(
            evaluate_all_with_prelude(parse(lex(
                u"(set-symbol! (quote x) (quote (1))) (append! x 2) x"))),
            expected)

    def test_append_bytestring(self):
        self.assertEqual(
            evaluate_all_with_prelude(parse(lex(
                u'(set-symbol! (quote x) #bytes("a")) (append! x 98) x'))),
            Bytestring([ord(c) for c in "ab"]))

    def test_append_string(self):
        self.assertEqual(
            evaluate_all_with_prelude(parse(lex(
                u'(set-symbol! (quote x) "a") (append! x \'b\') x'))),
            String(list(u"ab")))

    def test_append_returns_null(self):
        self.assertEqual(
            evaluate_with_prelude(parse_one(lex(
                u"(append! (quote ()) 1)"))),
            NULL)

    def test_append_arg_number(self):
        with self.assertRaises(ArityError):
            evaluate_with_prelude(parse_one(lex(
                u"(append! (quote ()))")))

        with self.assertRaises(ArityError):
            evaluate_with_prelude(parse_one(lex(
                u"(append! (quote ()) 0 1)")))

    def test_append_typeerror(self):
        # first argument must be a list
        with self.assertRaises(TrifleTypeError):
            evaluate_with_prelude(parse_one(lex(
                u"(append! #null 0)")))


class PushTest(unittest.TestCase):
    def test_push_list(self):
        expected = List([Integer(1)])
        
        self.assertEqual(
            evaluate_all_with_prelude(parse(lex(
                u"(set-symbol! (quote x) (quote ())) (push! x 1) x"))),
            expected)

    def test_push_bytestring(self):
        self.assertEqual(
            evaluate_all_with_prelude(parse(lex(
                u'(set-symbol! (quote x) #bytes("bc")) (push! x 97) x'))),
            Bytestring([ord(c) for c in b"abc"]))

    def test_push_string(self):
        self.assertEqual(
            evaluate_all_with_prelude(parse(lex(
                u'(set-symbol! (quote x) "bc") (push! x \'a\') x'))),
            String(list(u"abc")))

    def test_push_returns_null(self):
        self.assertEqual(
            evaluate_with_prelude(parse_one(lex(
                u"(push! (quote ()) 1)"))),
            NULL)

    def test_push_arg_number(self):
        with self.assertRaises(ArityError):
            evaluate_with_prelude(parse_one(lex(
                u"(push! (quote ()))")))

        with self.assertRaises(ArityError):
            evaluate_with_prelude(parse_one(lex(
                u"(push! (quote ()) 0 1)")))

    def test_push_typeerror(self):
        # first argument must be a list
        with self.assertRaises(TrifleTypeError):
            evaluate_with_prelude(parse_one(lex(
                u"(push! #null 0)")))


class NotTest(unittest.TestCase):
    def test_not_booleans(self):
        self.assertEqual(
            evaluate_with_prelude(parse_one(lex(u"(not #true)"))),
            FALSE)
        
        self.assertEqual(
            evaluate_with_prelude(parse_one(lex(u"(not #false)"))),
            TRUE)


class AndTest(unittest.TestCase):
    def test_and(self):
        self.assertEqual(
            evaluate_with_prelude(parse_one(lex(u"(and #true #true)"))),
            TRUE)
        self.assertEqual(
            evaluate_with_prelude(parse_one(lex(u"(and #true #false)"))),
            FALSE)
        self.assertEqual(
            evaluate_with_prelude(parse_one(lex(u"(and #false #true)"))),
            FALSE)
        self.assertEqual(
            evaluate_with_prelude(parse_one(lex(u"(and #false #false)"))),
            FALSE)
        
    def test_and_arity(self):
        self.assertEqual(
            evaluate_with_prelude(parse_one(lex(u"(and)"))),
            TRUE)

        self.assertEqual(
            evaluate_with_prelude(parse_one(lex(u"(and #true #true #true)"))),
            TRUE)

    def test_and_evaluation(self):
        """Statements should not be evaluated more than once."""
        self.assertEqual(
            evaluate_all_with_prelude(parse(lex(
                u"(set! x 0)"
                u"(and (do (inc! x) #true))"
                u"x"))),
            Integer(1))


class OrTest(unittest.TestCase):
    def test_or(self):
        self.assertEqual(
            evaluate_with_prelude(parse_one(lex(u"(or #true #true)"))),
            TRUE)
        self.assertEqual(
            evaluate_with_prelude(parse_one(lex(u"(or #true #false)"))),
            TRUE)
        self.assertEqual(
            evaluate_with_prelude(parse_one(lex(u"(or #false #true)"))),
            TRUE)
        self.assertEqual(
            evaluate_with_prelude(parse_one(lex(u"(or #false #false)"))),
            FALSE)
        
    def test_or_arity(self):
        self.assertEqual(
            evaluate_with_prelude(parse_one(lex(u"(or)"))),
            FALSE)

        self.assertEqual(
            evaluate_with_prelude(parse_one(lex(u"(or #true #true #true)"))),
            TRUE)

    def test_or_evaluation(self):
        """Statements should not be evaluated more than once."""
        self.assertEqual(
            evaluate_all_with_prelude(parse(lex(
                u"(set! x 0)"
                u"(or (do (inc! x) #true))"
                u"x"))),
            Integer(1))


class RestTest(unittest.TestCase):
    def test_rest(self):
        self.assertEqual(
            evaluate_with_prelude(parse_one(lex(u"(rest (list 1 2 3))"))),
            List([Integer(2), Integer(3)]))
        
    def test_rest_bytestring(self):
        self.assertEqual(
            evaluate_with_prelude(parse_one(lex(u'(rest #bytes("abc"))'))),
            Bytestring([ord(c) for c in b"bc"]))
        
    def test_rest_string(self):
        self.assertEqual(
            evaluate_with_prelude(parse_one(lex(u'(rest "abc")'))),
            String(list(u"bc")))
        
    def test_rest_empty_list(self):
        self.assertEqual(
            evaluate_with_prelude(parse_one(lex(u"(rest (list))"))),
            List())
        
        
class UnlessTest(unittest.TestCase):
    def test_unless_true(self):
        self.assertEqual(
            evaluate_with_prelude(parse_one(lex(u"(unless #true 1)"))),
            NULL)
        
    def test_unless_false(self):
        self.assertEqual(
            evaluate_with_prelude(parse_one(lex(u"(unless #false 1 2)"))),
            Integer(2))
        
class CaseTest(unittest.TestCase):
    def test_case_true(self):
        self.assertEqual(
            evaluate_with_prelude(parse_one(lex(u"(case (#true 1))"))),
            Integer(1))

    def test_case_first_match(self):
        self.assertEqual(
            evaluate_with_prelude(parse_one(lex(u"(case (#true 1) (#true 2))"))),
            Integer(1))

    def test_case_second_match(self):
        self.assertEqual(
            evaluate_with_prelude(parse_one(lex(u"(case (#false 1) (#true 2))"))),
            Integer(2))

    def test_clause_body_in_correct_scope(self):
        self.assertEqual(
            evaluate_with_prelude(parse_one(lex(u"(let (x 2) (case (#false 1) (#true x)))"))),
            Integer(2))


class RangeTest(unittest.TestCase):
    def test_range(self):
        self.assertEqual(
            evaluate_with_prelude(parse_one(lex(u"(range 5)"))),
            evaluate_with_prelude(parse_one(lex(u"(list 0 1 2 3 4)")))
        )


class InequalityTest(unittest.TestCase):
    def test_greater_than(self):
        self.assertEqual(
            evaluate_with_prelude(parse_one(lex(u"(> 2 1)"))),
            TRUE
        )
        self.assertEqual(
            evaluate_with_prelude(parse_one(lex(u"(> 2 2)"))),
            FALSE
        )
        self.assertEqual(
            evaluate_with_prelude(parse_one(lex(u"(> 2 3)"))),
            FALSE
        )

    def test_greater_or_equal(self):
        self.assertEqual(
            evaluate_with_prelude(parse_one(lex(u"(>= 2 1)"))),
            TRUE
        )
        self.assertEqual(
            evaluate_with_prelude(parse_one(lex(u"(>= 2 2)"))),
            TRUE
        )
        self.assertEqual(
            evaluate_with_prelude(parse_one(lex(u"(>= 2 3)"))),
            FALSE
        )
        
    def test_less_or_equal(self):
        self.assertEqual(
            evaluate_with_prelude(parse_one(lex(u"(<= 2 1)"))),
            FALSE
        )
        self.assertEqual(
            evaluate_with_prelude(parse_one(lex(u"(<= 2 2)"))),
            TRUE
        )
        self.assertEqual(
            evaluate_with_prelude(parse_one(lex(u"(<= 2 3)"))),
            TRUE
        )

    def test_incomparable_types(self):
        with self.assertRaises(TrifleTypeError):
            evaluate_with_prelude(parse_one(lex(u"(> 1 #null)")))

        with self.assertRaises(TrifleTypeError):
            evaluate_with_prelude(parse_one(lex(u"(>= 1 #null)")))

        with self.assertRaises(TrifleTypeError):
            evaluate_with_prelude(parse_one(lex(u"(<= 1 #null)")))

