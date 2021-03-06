from trifle_types import (Function, FunctionWithEnv, Lambda, Macro, Special,
                          Integer, Float, Fraction, RBigInt,
                          List, Hashmap, Keyword,
                          FileHandle, Bytestring, Character,
                          TRUE, FALSE, NULL, Symbol, String,
                          TrifleExceptionInstance, TrifleExceptionType,
                          is_equal)
from errors import (
    ArityError, changing_closed_handle, division_by_zero,
    wrong_type, file_not_found, value_error, missing_key,
)
from almost_python import deepcopy, copy, raw_input, list
from parameters import validate_parameters
from lexer import lex
from trifle_parser import parse
from arguments import check_args
from hashable import check_hashable


class SetSymbol(FunctionWithEnv):
    def call(self, args, env, stack):
        check_args(u"set-symbol!", args, 2, 2)

        variable_name = args[0]
        variable_value = args[1]

        if not isinstance(variable_name, Symbol):
            return TrifleExceptionInstance(
                wrong_type,
                u"The first argument to set-symbol! must be a symbol, but got: %s"
                % variable_name.repr())

        env.set(variable_name.symbol_name, variable_value)

        return NULL


class Let(Special):
    def call(self, args, env, stack):
        # TODO: we should take at least two arguments.
        check_args(u'let', args, 1)

        bindings = args[0]
        body = args[1:]

        if not isinstance(bindings, List):
            return TrifleExceptionInstance(
                wrong_type,
                u"let requires a list as its first argument, but got: %s"
                % bindings.repr()
            )

        for index, expression in enumerate(bindings.values):
            if index % 2 == 0:
                if not isinstance(expression, Symbol):
                    return TrifleExceptionInstance(
                        wrong_type,
                        u"Expected a symbol for a let-bound variable, but got: %s"
                        % expression.repr()
                    )

        if len(bindings.values) % 2 == 1:
            raise ArityError(
                u"no value given for let-bound variable: %s"
                % bindings.values[-1].repr())

        # Fix circular import by importing here.
        from environment import LetScope
        from evaluator import Frame
        
        frame = stack.peek()

        if frame.expression_index == 0:
            # We don't evaluate the let symbol.
            frame.expression_index += 1
            return None

        elif frame.expression_index == 1:
            # We evaluate each of the variable bindings and assign
            # them, allowing bindings to access previous bindings in
            # the same let block.
            if frame.let_assignment_index == 0:
                let_scope = LetScope({})
                let_env = env.with_nested_scope(let_scope)
                frame.let_environment = let_env
            else:
                let_env = frame.let_environment

            if frame.let_assignment_index * 2 >= len(bindings.values):
                # We've finished setting up the bindings. Assign the
                # last result into the environment.

                # Unless we had no bindings at all, assign the final binding.
                if frame.let_assignment_index > 0:
                    previous_sym = bindings.values[2 * (frame.let_assignment_index - 1)]
                    previous_value = frame.evalled.pop()

                    let_scope = let_env.scopes[-1]
                    let_scope.set(previous_sym.symbol_name, previous_value)
                
                frame.expression_index += 1
                return None

            if frame.let_assignment_index == 0:
                # Evaluate the first assignment.
                stack.push(Frame(bindings.values[1], let_env))
                frame.let_assignment_index += 1
                return None
            else:
                # Assign the previous result in the environment, and
                # evaluate the next.
                
                previous_sym = bindings.values[2 * (frame.let_assignment_index - 1)]
                previous_value = frame.evalled.pop()
                
                let_scope = let_env.scopes[-1]
                let_scope.set(previous_sym.symbol_name, previous_value)
                
                stack.push(Frame(bindings.values[2 * frame.let_assignment_index + 1], let_env))
                frame.let_assignment_index += 1
                return None
                
        elif frame.expression_index == 2:
            # Evaluate the body now we have all the assignments.
            stack.push(Frame(List(body), frame.let_environment, as_block=True))
            
            frame.expression_index += 1
            return None

        else:
            # Evalled body, just return the result
            return frame.evalled[-1]


class LambdaFactory(Special):
    """Return a fresh Lambda object every time it's called."""

    def call(self, args, env, stack):
        check_args(u'lambda', args, 1)

        parameters = args[0]

        error = validate_parameters(parameters)
        if error:
            return error

        lambda_body = List(args[1:])
        return Lambda(parameters, lambda_body, env)


# todo: support docstrings
class DefineMacro(Special):
    """Create a new macro object and bind it to the variable name given,
    in the global scope.

    """

    def call(self, args, env, stack):
        check_args(u'macro', args, 3)

        macro_name = args[0]
        parameters = args[1]
        
        if not isinstance(macro_name, Symbol):
            return TrifleExceptionInstance(
                wrong_type,
                u"macro name should be a symbol, but got: %s" %
                macro_name.repr())

        parameters = args[1]
        error = validate_parameters(parameters)

        if error:
            return error

        macro_body = List(args[2:])
        env.set_global(macro_name.symbol_name,
                       Macro(macro_name.symbol_name, parameters, macro_body))

        return NULL


# TODO: unit test
# TODOC
# TODO: add an expand-all-macros special too.
# TODO: Could we make this a function?
class ExpandMacro(Special):
    """Given an expression that is a macro call, expand it one step and
    return the resulting (unevaluated) expression.

    """
    def call(self, args, env, stack):
        check_args(u'expand-macro', args, 1)

        expr = args[0]

        if not isinstance(expr, List):
            return TrifleExceptionInstance(
                wrong_type,
                u"The first argument to expand-macro must be a list, but got: %s" % args[0].repr())

        if not expr.values:
            return TrifleExceptionInstance(
                wrong_type,
                u"The first argument to expand-macro must be a non-empty list.")

        macro_name = expr.values[0]

        from evaluator import evaluate, expand_macro
        macro = evaluate(macro_name, env)

        if not isinstance(macro, Macro):
            return TrifleExceptionInstance(
                wrong_type,
                u"Expected a macro, but got: %s" % macro.repr())

        macro_args = expr.values[1:]
        return expand_macro(macro, macro_args, env)


# todo: it would be nice to define this as a trifle macro using a 'literal' primitive
# (e.g. elisp defines backquote in terms of quote)
class Quote(Special):
    def is_unquote(self, expression):
        """Is this expression of the form (unquote expression)?"""
        if not isinstance(expression, List):
            return False

        if not expression.values:
            return False

        list_head = expression.values[0]
        if not isinstance(list_head, Symbol):
            return False

        if not list_head.symbol_name == u'unquote':
            return False

        return True

    def is_unquote_star(self, expression):
        """Is this expression of the form (unquote* expression)?"""
        if not isinstance(expression, List):
            return False

        if not expression.values:
            return False

        list_head = expression.values[0]
        if not isinstance(list_head, Symbol):
            return False

        if not list_head.symbol_name == u'unquote*':
            return False

        return True
    
    # todo: fix the potential stack overflow
    def evaluate_unquote_calls(self, expression, env, stack):
        from evaluator import evaluate
        if isinstance(expression, List):
            for index, item in enumerate(copy(expression).values):
                if self.is_unquote(item):
                    # TODO: this is calling repr but including the function call itself
                    if len(item.values) != 2:
                        raise ArityError(
                            u"unquote takes 1 argument, but got: %s" % item.repr())
            
                    unquote_argument = item.values[1]
                    expression.values[index] = evaluate(unquote_argument, env)
                    
                elif self.is_unquote_star(item):
                    if len(item.values) != 2:
                        raise ArityError(
                            u"unquote* takes 1 argument, but got: %s" % item.repr())
            
                    unquote_argument = item.values[1]
                    values_list = evaluate(unquote_argument, env)

                    if not isinstance(values_list, List):
                        return TrifleExceptionInstance(
                            wrong_type,
                            u"unquote* must be used with a list, but got a %s" % values_list.repr())

                    # Splice in the result of evaluating the unquote* argument
                    expression.values = expression.values[:index] + values_list.values + expression.values[index+1:]

                elif isinstance(item, List):
                    # recurse the nested list
                    result = self.evaluate_unquote_calls(item, env, stack)

                    if isinstance(result, TrifleExceptionInstance):
                        return result

        return expression
    
    def call(self, args, env, stack):
        check_args(u'quote', args, 1, 1)

        if isinstance(args[0], List) and args[0].values:
            list_head = args[0].values[0]

            if isinstance(list_head, Symbol):
                if list_head.symbol_name == u"unquote*":
                    return TrifleExceptionInstance(
                        value_error,
                        u"Can't call unquote* at top level of quote expression, you need to be inside a list.")

        result = self.evaluate_unquote_calls(List([deepcopy(args[0])]), env, stack)

        if isinstance(result, TrifleExceptionInstance):
            return result
        elif isinstance(result, List):
            return result.values[0]


class If(Special):
    def call(self, args, environment, stack):
        check_args(u'if', args, 3, 3)

        condition = args[0]
        then = args[1]
        otherwise = args[2]

        frame = stack.peek()

        # TODO: Move Frame to separate module to fix the cyclic import.
        from evaluator import Frame
        
        if frame.expression_index == 0:
            # We don't evaluate the if symbol.
            frame.expression_index += 1
            return None

        elif frame.expression_index == 1:
            # Evaluate the condition.
            stack.push(Frame(condition, environment))

            frame.expression_index += 1
            return None

        elif frame.expression_index == 2:
            # We've evaluated the condition, so either evaluate 'then'
            # or 'otherwise' depending on the return value.
            evalled_condition = frame.evalled[-1]
            
            if evalled_condition == TRUE:
                stack.push(Frame(then, environment))
                
                frame.expression_index += 1
                return None

            elif evalled_condition == FALSE:
                stack.push(Frame(otherwise, environment))
                
                frame.expression_index += 2
                return None

            else:
                return TrifleExceptionInstance(
                    wrong_type,
                    u"The first argument to if must be a boolean, but got: %s" %
                    evalled_condition.repr())
                
        else:
            # We've evaluated the condition and either 'then' or
            # 'otherwise', so pop this frame and return.
            return frame.evalled[-1]


class While(Special):
    def call(self, args, env, stack):
        check_args(u'while', args, 1)

        condition = args[0]
        body = List(args[1:])

        frame = stack.peek()

        from evaluator import Frame

        if frame.expression_index == 0:
            # We don't evaluate the while symbol.
            frame.expression_index += 1
            return None

        elif frame.expression_index == 1:
            # Evaluate the condition.
            stack.push(Frame(condition, env))

            frame.expression_index += 1
            return None

        elif frame.expression_index == 2:
            # We've evaluated the condition, so either evaluate the body, or return.
            evalled_condition = frame.evalled[-1]
            
            if evalled_condition == TRUE:
                stack.push(Frame(body, env, as_block=True))

                # Once we've evaluated the body, we should evaluate
                # the condition again.
                frame.expression_index = 1

                return None

            elif evalled_condition == FALSE:
                # while loops always return #null when done.
                return NULL

            else:
                return TrifleExceptionInstance(
                    wrong_type,
                    u"The first argument to while must be a boolean, but got: %s" %
                    evalled_condition.repr())
        

# todo: implement in prelude in terms of stdin and stdout
class Input(Function):
    def call(self, args):
        check_args(u'input', args, 1, 1)
        prefix = args[0]

        if not isinstance(prefix, String):
            return TrifleExceptionInstance(
                wrong_type,
                u"The first argument to input must be a string, but got: %s"
                % prefix.repr())

        user_input = raw_input(prefix.as_unicode())
        return String([char for char in user_input])


class Same(Function):
    def call(self, args):
        check_args(u'same?', args, 2, 2)

        # Sadly, we can't access .__class__ in RPython.
        # TODO: proper symbol interning.
        if isinstance(args[0], Symbol):
            if isinstance(args[1], Symbol):
                if args[0].symbol_name == args[1].symbol_name:
                    return TRUE

            return FALSE

        if args[0] is args[1]:
            return TRUE
        else:
            return FALSE


# TODO: Is there a better place in the docs for this, rather than under booleans?
# We're inconsistent between grouping by input type or output type.
class Equal(Function):
    def call(self, args):
        check_args(u'equal?', args, 2, 2)

        if is_equal(args[0], args[1]):
            return TRUE
        else:
            return FALSE


class FreshSymbol(Function):
    def __init__(self):
        self.count = 1

    def call(self, args):
        check_args(u'fresh-symbol', args, 0, 0)

        symbol_name = u"%d-unnamed" % self.count
        self.count += 1

        return Symbol(symbol_name)


def coerce_numbers(nums):
    """Given a list of Trifle numbers, coerce them all to be the same
    type. Convert to the lower common denominator if necessary.

    Assumes all elements are numbers.

    >>> coerce_numbers([Integer.fromint(1)])
    [Integer.fromint(1)]
    >>> coerce_numbers([Fraction(RBigInt.fromint(1), RBigInt.fromint(2)), Float(1.0)])
    [Float(0.5), Float(1.0)]

    """
    contains_floats = False
    contains_fractions = False
    
    for num in nums:
        if isinstance(num, Float):
            contains_floats = True
            break
        elif isinstance(num, Fraction):
            contains_fractions = True

    result = []
    if contains_floats:

        for num in nums:
            if isinstance(num, Integer):
                # TODO: This could overflow if the integer is outside
                # the range of acceptable floats.
                result.append(Float(num.bigint_value.tofloat()))
            elif isinstance(num, Fraction):
                # TODO: Carefully document and unit test the corner cases
                # here.
                result.append(Float(num.numerator.tofloat() / num.denominator.toint()))
            elif isinstance(num, Float):
                result.append(num)

        return result
        
    elif contains_fractions:
        for num in nums:
            if isinstance(num, Integer):
                # TODO: we need abitrary sized fractions too.
                result.append(Fraction(num.bigint_value, RBigInt.fromint(1)))
            elif isinstance(num, Fraction):
                result.append(num)

        return result

    else:
        return nums


class Add(Function):
    def call(self, args):
        float_args = False
        fraction_args = False
        
        for arg in args:
            if isinstance(arg, Integer):
                pass
            elif isinstance(arg, Fraction):
                fraction_args = True
            elif isinstance(arg, Float):
                float_args = True
            else:
                return TrifleExceptionInstance(
                    wrong_type,
                    u"+ requires numbers, but got: %s." % arg.repr())

        args = coerce_numbers(args)

        if float_args:
            total = 0.0
            for arg in args:
                total += arg.float_value

            return Float(total)

        elif fraction_args:
            total = Fraction(RBigInt.fromint(0), RBigInt.fromint(1))

            for arg in args:
                # a/b + c/d == (ad + bc) / bd
                total = Fraction(
                    total.numerator.mul(arg.denominator).add(arg.numerator.mul(total.denominator)),
                    arg.denominator.mul(total.denominator)
                )

            if total.denominator.eq(RBigInt.fromint(1)):
                return Integer(total.numerator)

            return total

        else:
            # Just integers.
            total = RBigInt.fromint(0)
            for arg in args:
                total = total.add(arg.bigint_value)
            return Integer(total)


class Subtract(Function):
    def call(self, args):
        float_args = False
        fraction_args = False
        
        for arg in args:
            if isinstance(arg, Integer):
                pass
            elif isinstance(arg, Fraction):
                fraction_args = True
            elif isinstance(arg, Float):
                float_args = True
            else:
                return TrifleExceptionInstance(
                    wrong_type,
                    u"- requires numbers, but got: %s." % arg.repr())

        if not args:
            return Integer.fromint(0)

        if len(args) == 1:
            if isinstance(args[0], Integer):
                return Integer(args[0].bigint_value.neg())
            elif isinstance(args[0], Fraction):
                return Fraction(args[0].numerator.neg(), args[0].denominator)
            else:
                return Float(-args[0].float_value)

        args = coerce_numbers(args)

        if float_args:
            total = args[0].float_value
                
            for arg in args[1:]:
                total -= arg.float_value

            return Float(total)

        elif fraction_args:
            total = args[0]
                
            for arg in args[1:]:
                # a/b - c/d == (ad - bc) / bd
                total = Fraction(
                    total.numerator.mul(arg.denominator).sub(arg.numerator.mul(total.denominator)),
                    arg.denominator.mul(total.denominator)
                )

            if total.denominator.eq(RBigInt.fromint(1)):
                return Integer(total.numerator)

            return total

        else:
            total = args[0].bigint_value
            for arg in args[1:]:
                total = total.sub(arg.bigint_value)
            return Integer(total)


class Multiply(Function):
    def call(self, args):
        float_args = False
        fraction_args = False
        
        for arg in args:
            if isinstance(arg, Integer):
                pass
            elif isinstance(arg, Fraction):
                fraction_args = True
            elif isinstance(arg, Float):
                float_args = True
            else:
                return TrifleExceptionInstance(
                    wrong_type,
                    u"* requires numbers, but got: %s." % arg.repr())

        args = coerce_numbers(args)

        if float_args:
            product = 1.0
            for arg in args:
                product *= arg.float_value

            return Float(product)

        elif fraction_args:
            product = Fraction(RBigInt.fromint(1), RBigInt.fromint(1))

            for arg in args:
                product = Fraction(
                    product.numerator.mul(arg.numerator),
                    product.denominator.mul(arg.denominator),
                )

            # TODO: It would be convenient to have RBIGINT_ZERO and RBIGINT_ONE
            # even if we don't cache small numbers the way Python does.
            if product.denominator.eq(RBigInt.fromint(1)):
                return Integer(product.numerator)

            return product

        else:
            product = RBigInt.fromint(1)
            for arg in args:
                product = product.mul(arg.bigint_value)
            return Integer(product)


class Divide(Function):
    def call(self, args):
        check_args(u'/', args, 2)

        float_args = False
        
        for arg in args:
            if isinstance(arg, Integer):
                pass
            elif isinstance(arg, Fraction):
                pass
            elif isinstance(arg, Float):
                float_args = True
            else:
                return TrifleExceptionInstance(
                    wrong_type,
                    u"/ requires numbers, but got: %s." % arg.repr())

        args = coerce_numbers(args)

        if float_args:
            quotient = args[0].float_value

            for arg in args[1:]:
                try:
                    quotient /= arg.float_value
                except ZeroDivisionError:
                    return TrifleExceptionInstance(
                        division_by_zero,
                        u"Divided %f by %s" % (quotient, arg.repr()))

            return Float(quotient)

        else:
            if isinstance(args[0], Integer):
                quotient = Fraction(args[0].bigint_value, RBigInt.fromint(1))
            elif isinstance(args[0], Fraction):
                quotient = args[0]
            else:
                # Never happens, but to keep RPython happy.
                quotient = Fraction(RBigInt.fromint(1), RBigInt.fromint(1))
                
            for arg in args[1:]:
                if isinstance(arg, Integer):
                    if arg.bigint_value.eq(RBigInt.fromint(0)):
                        return TrifleExceptionInstance(
                            division_by_zero,
                            u"Divided %s by %s" % (quotient.repr(), arg.repr()))
                    
                    quotient = Fraction(
                        quotient.numerator, quotient.denominator.mul(arg.bigint_value)
                    )

                elif isinstance(arg, Fraction):
                    # Since fractions are always non-zero, we can't get a
                    # zero division error here.

                    # a/b / b/c == ac/bd
                    quotient = Fraction(
                        quotient.numerator.mul(arg.denominator),
                        quotient.denominator.mul(arg.numerator),
                    )

            if quotient.denominator.eq(RBigInt.fromint(1)):
                return Integer(quotient.numerator)

            return quotient
            

# TODO: it would be nice to support floats too
class Mod(Function):
    def call(self, args):
        check_args(u'mod', args, 2, 2)

        for arg in args:
            if not isinstance(arg, Integer):
                return TrifleExceptionInstance(
                    wrong_type,
                    u"mod requires integers, but got: %s." % arg.repr())

        if args[1].bigint_value.eq(RBigInt.fromint(0)):
            return TrifleExceptionInstance(
                division_by_zero,
                u"Divided by zero: %s" % args[1].repr())

        return Integer(args[0].bigint_value.mod(args[1].bigint_value))


class Div(Function):
    """Integer division. Note this differs from Python's //, which is
    floor division. In Python:

    >>> 4.5 // 1.5
    3.0

    """
    def call(self, args):
        check_args(u'div', args, 2, 2)

        for arg in args:
            if not isinstance(arg, Integer):
                return TrifleExceptionInstance(
                    wrong_type,
                    u"div requires integers, but got: %s." % arg.repr())

        if args[1].bigint_value.eq(RBigInt.fromint(0)):
            return TrifleExceptionInstance(
                division_by_zero,
                u"Divided by zero: %s" % args[1].repr())

        return Integer(args[0].bigint_value.floordiv(args[1].bigint_value))
            

class LessThan(Function):
    def call(self, args):
        check_args(u'<', args, 2)

        float_args = False
        fraction_args = False

        for arg in args:
            if isinstance(arg, Integer):
                pass
            elif isinstance(arg, Fraction):
                fraction_args = True
            elif isinstance(arg, Float):
                float_args = True
            else:
                return TrifleExceptionInstance(
                    wrong_type,
                    u"< requires numbers, but got: %s." % arg.repr())

        args = coerce_numbers(args)
                
        previous_number = args[0]
        if float_args:

            for arg in args[1:]:
                if not previous_number.float_value < arg.float_value:
                    return FALSE

                previous_number = arg
                    
            return TRUE

        elif fraction_args:
            
            for arg in args[1:]:
                # To find out if a/b is less than c/d, we compare whether
                # ad < bc. This is safe because b and d are always positive.
                ad = previous_number.numerator.mul(arg.denominator)
                bc = arg.numerator.mul(previous_number.denominator)

                if not ad.lt(bc):
                    return FALSE

                previous_number = arg
                    
            return TRUE

        else:
            # Only integers.
            for arg in args[1:]:
                if not previous_number.bigint_value.lt(arg.bigint_value):
                    return FALSE

                previous_number = arg

            return TRUE


class SymbolPredicate(Function):
    def call(self, args):
        check_args(u'symbol?', args, 1, 1)
        value = args[0]

        if isinstance(value, Symbol):
            return TRUE
        else:
            return FALSE


# TODO: Just write a generic function that returns the type of its argument.
class ListPredicate(Function):
    def call(self, args):
        check_args(u'list?', args, 1, 1)
        value = args[0]

        if isinstance(value, List):
            return TRUE
        else:
            return FALSE


class HashmapPredicate(Function):
    def call(self, args):
        check_args(u'hashmap?', args, 1, 1)
        value = args[0]

        if isinstance(value, Hashmap):
            return TRUE
        else:
            return FALSE


class StringPredicate(Function):
    def call(self, args):
        check_args(u'string?', args, 1, 1)
        value = args[0]

        if isinstance(value, String):
            return TRUE
        else:
            return FALSE


class BytestringPredicate(Function):
    def call(self, args):
        check_args(u'bytestring?', args, 1, 1)
        value = args[0]

        if isinstance(value, Bytestring):
            return TRUE
        else:
            return FALSE


class CharacterPredicate(Function):
    def call(self, args):
        check_args(u'character?', args, 1, 1)
        value = args[0]

        if isinstance(value, Character):
            return TRUE
        else:
            return FALSE


class GetIndex(Function):
    def call(self, args):
        check_args(u'get-index', args, 2, 2)
        sequence = args[0]
        index = args[1]

        if isinstance(sequence, List):
            sequence_length = RBigInt.fromint(len(sequence.values))
        elif isinstance(sequence, Bytestring):
            sequence_length = RBigInt.fromint(len(sequence.byte_value))
        elif isinstance(sequence, String):
            sequence_length = RBigInt.fromint(len(sequence.string))
        else:
            return TrifleExceptionInstance(
                wrong_type,
                u"the first argument to get-index must be a sequence, but got: %s"
                % sequence.repr())

        if not isinstance(index, Integer):
            return TrifleExceptionInstance(
                wrong_type,
                u"the second argument to get-index must be an integer, but got: %s"
                % index.repr())

        if sequence_length.eq(RBigInt.fromint(0)):
            return TrifleExceptionInstance(
                value_error,
                u"can't call get-item on an empty sequence")

        # todo: use a separate error class for index errors
        if index.bigint_value.ge(sequence_length):
            return TrifleExceptionInstance(
                value_error,
                u"the sequence has %s items, but you asked for index %s"
                % (unicode(sequence_length.str()), index.repr()))

        if index.bigint_value.lt(sequence_length.neg()):
            return TrifleExceptionInstance(
                value_error,
                u"Can't get index %s of a %s element sequence (must be -%s or higher)"
                % (index.repr(), unicode(sequence_length.str()), unicode(sequence_length.str())))

        if isinstance(sequence, List):
            return sequence.values[index.bigint_value.toint()]
        elif isinstance(sequence, Bytestring):
            return Integer.fromint(sequence.byte_value[index.bigint_value.toint()])
        elif isinstance(sequence, String):
            return Character(sequence.string[index.bigint_value.toint()])


class GetKey(Function):
    def call(self, args):
        check_args(u'get-key', args, 2, 2)
        hashmap = args[0]
        key = args[1]

        if not isinstance(hashmap, Hashmap):
            return TrifleExceptionInstance(
                wrong_type,
                u"the first argument to get-key must be a hashmap, but got: %s"
                % hashmap.repr())

        value = hashmap.dict.get(key, None)

        if value is None:
            return TrifleExceptionInstance(
                missing_key,
                u"Key %s not found in hashmap" % key.repr()
            )

        return value


class SetKey(Function):
    def call(self, args):
        check_args(u'set-key!', args, 3, 3)
        hashmap = args[0]
        key = args[1]
        value = args[2]

        if not isinstance(hashmap, Hashmap):
            return TrifleExceptionInstance(
                wrong_type,
                u"the first argument to set-key! must be a hashmap, but got: %s"
                % hashmap.repr())

        is_hashable_error = check_hashable([key])
        if isinstance(is_hashable_error, TrifleExceptionInstance):
            return is_hashable_error

        hashmap.dict[key] = value
        return NULL


class GetItems(Function):
    def call(self, args):
        check_args(u'get-items', args, 1, 1)
        hashmap = args[0]

        if not isinstance(hashmap, Hashmap):
            return TrifleExceptionInstance(
                wrong_type,
                u"the first argument to get-items must be a hashmap, but got: %s"
                % hashmap.repr())

        items = List()
        for key, value in hashmap.dict.iteritems():
            items.append(List([key, value]))

        return items


class Length(Function):
    def call(self, args):
        check_args(u'length', args, 1, 1)
        sequence = args[0]

        if isinstance(sequence, List):
            return Integer.fromint(len(sequence.values))
        elif isinstance(sequence, Bytestring):
            return Integer.fromint(len(sequence.byte_value))
        elif isinstance(sequence, String):
            return Integer.fromint(len(sequence.string))

        return TrifleExceptionInstance(
            wrong_type,
            u"the first argument to length must be a sequence, but got: %s"
            % sequence.repr())


class SetIndex(Function):
    def call(self, args):
        check_args(u'set-index!', args, 3, 3)
        sequence = args[0]
        index = args[1]
        value = args[2]

        if isinstance(sequence, List):
            sequence_length = RBigInt.fromint(len(sequence.values))
        elif isinstance(sequence, Bytestring):
            sequence_length = RBigInt.fromint(len(sequence.byte_value))
        elif isinstance(sequence, String):
            sequence_length = RBigInt.fromint(len(sequence.string))
        else:
            return TrifleExceptionInstance(
                wrong_type,
                u"the first argument to set-index! must be a sequence, but got: %s"
                % sequence.repr())

        if not isinstance(index, Integer):
            return TrifleExceptionInstance(
                wrong_type,
                u"the second argument to set-index! must be an integer, but got: %s"
                % index.repr())

        if sequence_length.eq(RBigInt.fromint(0)):
            return TrifleExceptionInstance(
                value_error,
                u"can't call set-index! on an empty sequence")

        # TODO: use a separate error class for index error
        if index.bigint_value.ge(sequence_length):
            return TrifleExceptionInstance(
                value_error,
                # TODO: pluralisation (to avoid '1 items')
                u"the sequence has %s items, but you asked to set index %s"
                % (unicode(sequence_length.str()), index.repr()))

        if index.bigint_value.lt(sequence_length.neg()):
            return TrifleExceptionInstance(
                value_error,
                u"Can't set index %s of a %s element sequence (must be -%s or higher)"
                % (index.repr(), unicode(sequence_length.str()), unicode(sequence_length.str())))

        if isinstance(sequence, List):
            sequence.values[index.bigint_value.toint()] = value
        elif isinstance(sequence, Bytestring):
            if not isinstance(value, Integer):
                return TrifleExceptionInstance(
                    wrong_type,
                    u"Permitted values inside bytestrings are only integers between 0 and 255, but got: %s"
                    % value.repr())

            if value.bigint_value.lt(RBigInt.fromint(0)) or value.bigint_value.gt(RBigInt.fromint(255)):
                return TrifleExceptionInstance(
                    value_error,
                    u"Permitted values inside bytestrings are only integers between 0 and 255, but got: %s"
                    % value.repr())

            sequence.byte_value[index.bigint_value.toint()] = value.bigint_value.toint()
        elif isinstance(sequence, String):
            if not isinstance(value, Character):
                return TrifleExceptionInstance(
                    wrong_type,
                    u"Permitted values inside strings are only characters, but got: %s"
                    % value.repr())

            # TODO: what if the list contains more than 2 ** 32 items?
            # We should remove all uses of .toint, it's risky.
            sequence.string[index.bigint_value.toint()] = value.character

        return NULL


class Insert(Function):
    def call(self, args):
        check_args(u'insert!', args, 3, 3)
        sequence = args[0]
        index = args[1]
        value = args[2]

        if isinstance(sequence, List):
            # TODO: what if the sequence has more than 2**32 items?
            sequence_length = RBigInt.fromint(len(sequence.values))
        elif isinstance(sequence, Bytestring):
            sequence_length = RBigInt.fromint(len(sequence.byte_value))
        elif isinstance(sequence, String):
            sequence_length = RBigInt.fromint(len(sequence.string))
        else:
            return TrifleExceptionInstance(
                wrong_type,
                u"the first argument to insert! must be a sequence, but got: %s"
                % sequence.repr())

        if not isinstance(index, Integer):
            return TrifleExceptionInstance(
                wrong_type,
                u"the second argument to insert! must be an integer, but got: %s"
                % index.repr())

        # todo: use a separate error class for index error
        if index.bigint_value.gt(sequence_length):
            return TrifleExceptionInstance(
                value_error,
                u"the sequence has %s items, but you asked to insert at index %s"
                % (unicode(sequence_length.str()), index.repr()))

        if index.bigint_value.lt(sequence_length.neg()):
            return TrifleExceptionInstance(
                value_error,
                u"Can't set index %s of a %s element sequence (must be -%s or higher)"
                % (index.repr(), unicode(sequence_length.str()), unicode(sequence_length.str())))

        target_index = index.bigint_value
        if target_index.lt(RBigInt.fromint(0)):
            target_index = target_index.mod(sequence_length)

        target_index_int = target_index.toint()
        # We know that this is always non-negative, but RPython
        # cannot prove it. This if statement is just to keep
        # RPython happy.
        if target_index_int < 0:
            target_index_int = 0

        if isinstance(sequence, List):
            sequence.values.insert(target_index_int, value)
        elif isinstance(sequence, Bytestring):
            if not isinstance(value, Integer):
                return TrifleExceptionInstance(
                    wrong_type,
                    u"Permitted values inside bytestrings are only integers between 0 and 255, but got: %s"
                    % value.repr())

            if value.bigint_value.lt(RBigInt.fromint(0)) or value.bigint_value.gt(RBigInt.fromint(255)):
                return TrifleExceptionInstance(
                    value_error,
                    u"Permitted values inside bytestrings are only integers between 0 and 255, but got: %s"
                    % value.repr())

            sequence.byte_value.insert(target_index_int, value.bigint_value.toint())
        elif isinstance(sequence, String):
            if not isinstance(value, Character):
                return TrifleExceptionInstance(
                    wrong_type,
                    u"Permitted values inside strings are only characters, but got: %s"
                    % value.repr())

            sequence.string.insert(target_index_int, value.character)

        return NULL


class Parse(Function):
    def call(self, args):
        check_args(u'parse', args, 1, 1)
        program_string = args[0]

        if not isinstance(program_string, String):
            return TrifleExceptionInstance(
                wrong_type,
                u"the first argument to parse must be a string, but got: %s"
                % program_string.repr())

        tokens = lex(program_string.as_unicode())

        if isinstance(tokens, TrifleExceptionInstance):
            return tokens
        
        return parse(tokens)


# todo: consider allowing the user to pass in an environment for sandboxing
class Eval(FunctionWithEnv):
    def call(self, args, env, stack):
        check_args(u'eval', args, 1, 1)

        frame = stack.peek()

        # Note that the expression index will already be 2, since
        # evaluate_function_call will have iterated over our
        # arguments.
        from evaluator import Frame

        # Evaluate our argument.
        stack.push(Frame(args[0], env))

        # Incrementing the expression_index will result in evaluate()
        # just returning frame.evalled, so Eval.call will not be called again.
        frame.expression_index += 1
        return None

class Call(FunctionWithEnv):
    def call(self, args, env, stack):
        check_args(u'call', args, 2, 2)
        function = args[0]
        arguments = args[1]

        # Sadly, RPython doesn't support isinstance(x, (A, B)).
        if not (isinstance(function, Function) or isinstance(function, FunctionWithEnv)
                or isinstance(function, Lambda)):
            return TrifleExceptionInstance(
                wrong_type,
                u"the first argument to call must be a function, but got: %s"
                % function.repr())

        if not isinstance(arguments, List):
            return TrifleExceptionInstance(
                wrong_type,
                u"the second argument to call must be a list, but got: %s"
                % arguments.repr())

        frame = stack.peek()

        # Note that the expression index will already be 3, since
        # evaluate_function_call will have iterated over our
        # arguments. We just increment from there.
        if frame.expression_index == 3:
            # Build an equivalent expression
            expression = List([function] + arguments.values)

            from evaluator import Frame
            new_frame = Frame(expression, env)

            # Ensure that we don't evaluate the arguments to the function
            # a second time.
            new_frame.expression_index = len(arguments.values) + 1
            new_frame.evalled = [function] + arguments.values

            # Call the function.
            stack.push(new_frame)

            # Increment expression_index to show there's nothing left to do here.
            frame.expression_index += 1
            return None


# todo: rename to DefinedPredicate
class Defined(FunctionWithEnv):
    def call(self, args, env, stack):
        check_args(u'defined?', args, 1, 1)
        symbol = args[0]

        if not isinstance(symbol, Symbol):
            return TrifleExceptionInstance(
                wrong_type,
                u"the first argument to defined? must be a symbol, but got: %s"
                % symbol.repr())

        if env.contains(symbol.symbol_name):
            return TRUE
        else:
            return FALSE


# TODO: error on a file we can't write to
# TODO: error when we run out of file handles
# TODO: other errors the file system can throw at us
class Open(Function):
    def call(self, args):
        check_args(u'open', args, 2, 2)
        path = args[0]

        if not isinstance(path, String):
            return TrifleExceptionInstance(
                wrong_type,
                u"the first argument to open must be a string, but got: %s"
                % path.repr())

        flag = args[1]

        if not isinstance(flag, Keyword):
            return TrifleExceptionInstance(
                wrong_type,
                u"the second argument to open must be a keyword, but got: %s"
                % flag.repr())

        if flag.symbol_name == u'write':
            handle = open(path.as_unicode().encode('utf-8'), 'w')
        elif flag.symbol_name == u'read':
            try:
                handle = open(path.as_unicode().encode('utf-8'), 'r')
            except IOError as e:
                # TODO: Fix RPython error that stops us inspecting .errno.
                # This will throw on other IOErrors, such as permission problems.
                return TrifleExceptionInstance(
                    file_not_found,
                    u"No file found: %s" % path.as_unicode())
                # if e.errno == 2:
                #     raise FileNotFound(u"No file found: %s" % path.as_unicode())
                # else:
                #     raise
        else:
            return TrifleExceptionInstance(
                value_error,
                u"Invalid flag for open: :%s" % flag.symbol_name)

        return FileHandle(path.as_unicode().encode('utf-8'), handle, flag)


class Close(Function):
    def call(self, args):
        check_args(u'close!', args, 1, 1)
        handle = args[0]

        if not isinstance(handle, FileHandle):
            return TrifleExceptionInstance(
                wrong_type,
                u"the first argument to close! must be a file handle, but got: %s"
                % handle.repr())

        if handle.is_closed:
            return TrifleExceptionInstance(
                changing_closed_handle,
                # TODO: This assumes the file name is always UTF-8, which may not be
                # true if the user has chosen a different file system encoding.
                u"File handle for %s is already closed." % handle.file_name.decode('utf-8'))
        else:
            handle.close()

        return NULL


# TODO: specify a limit for how much to read.
class Read(Function):
    def call(self, args):
        check_args(u'read', args, 1, 1)
        handle = args[0]

        if not isinstance(handle, FileHandle):
            return TrifleExceptionInstance(
                wrong_type,
                u"the first argument to read must be a file handle, but got: %s"
                % handle.repr())

        return Bytestring([ord(c) for c in handle.file_handle.read()])


class Write(Function):
    def call(self, args):
        check_args(u'write!', args, 2, 2)
        handle = args[0]

        if not isinstance(handle, FileHandle):
            return TrifleExceptionInstance(
                wrong_type,
                u"the first argument to write! must be a file handle, but got: %s"
                % handle.repr())

        if handle.mode.symbol_name != u"write":
            return TrifleExceptionInstance(
                value_error,
                u"%s is a read-only file handle, you can't write to it."
                % handle.repr())

        if handle.is_closed:
            return TrifleExceptionInstance(
                changing_closed_handle,
                u"File handle for %s is already closed." % handle.file_name.decode('utf-8'))

        to_write = args[1]

        if not isinstance(to_write, Bytestring):
            return TrifleExceptionInstance(
                wrong_type,
                u"the second argument to write! must be a bytes, but got: %s"
                % to_write.repr())

        handle.write("".join([chr(c) for c in to_write.byte_value]))

        return NULL


class Flush(Function):
    def call(self, args):
        check_args(u'flush', args, 1, 1)
        handle = args[0]

        if not isinstance(handle, FileHandle):
            return TrifleExceptionInstance(
                wrong_type,
                u"the first argument to flush must be a file handle, but got: %s"
                % handle.repr())

        if handle.is_closed:
            return TrifleExceptionInstance(
                changing_closed_handle,
                u"File handle for %s is already closed." % handle.file_name.decode('utf-8'))

        handle.flush()

        return NULL


# TODO: take a second argument that specifies the encoding.
class Encode(Function):
    def call(self, args):
        check_args(u'encode', args, 1, 1)
        string = args[0]

        if not isinstance(string, String):
            return TrifleExceptionInstance(
                wrong_type,
                u"the first argument to encode must be a string, but got: %s"
                % string.repr())

        string_as_bytestring = string.as_unicode().encode('utf-8')
        return Bytestring([ord(c) for c in string_as_bytestring])


# TODO: take a second argument that specifies the encoding.
# TODO: throw an exception on bytes that aren't valid UTF-8.
class Decode(Function):
    def call(self, args):
        check_args(u'decode', args, 1, 1)
        bytestring = args[0]

        if not isinstance(bytestring, Bytestring):
            return TrifleExceptionInstance(
                wrong_type,
                u"the first argument to decode must be bytes, but got: %s"
                % bytestring.repr())

        bytestring_chars = [chr(c) for c in bytestring.byte_value]
        py_unicode = b"".join(bytestring_chars).decode('utf-8')
        return String([char for char in py_unicode])


# TODO: take an extra argument for return codes (and check against the maximum legal value).
# TODOC
class Exit(Function):
    def call(self, args):
        check_args(u'exit!', args, 0, 0)
        raise SystemExit()


class Try(Special):
    def call(self, args, env, stack):
        # TODO: multiple catch blocks, finally, resuming.
        check_args(u'try', args, 5, 5)

        body = args[0]
        catch_keyword = args[1]
        raw_exception_type = args[2]
        exception_binding = args[3]

        if not isinstance(catch_keyword, Keyword) or catch_keyword.symbol_name != u"catch":
            return TrifleExceptionInstance(
                wrong_type,
                u"The second argument to try must be :catch, but got: %s"
                % catch_keyword.repr())

        if not isinstance(exception_binding, Symbol):
            return TrifleExceptionInstance(
                wrong_type,
                u"The fourth argument to try must be a symbol, but got: %s"
                % exception_binding.repr())

        frame = stack.peek()
        from evaluator import Frame

        # Note that we increment the expression index even though
        # we evaluate the expected exception type first.
        if frame.expression_index == 0:
            # First, we evaluate the exception type.
            stack.push(Frame(raw_exception_type, env))

            frame.expression_index = 1
            return None

        elif frame.expression_index == 1:
            exception_type = frame.evalled[-1]

            if not isinstance(exception_type, TrifleExceptionType):
                return TrifleExceptionInstance(
                    wrong_type,
                    u"Expected a trifle exception type for :catch, but got: %s"
                    % exception_type.repr())

            # Mark the current frame as something we can come back to
            # if we encounter an error.
            frame.catch_error = exception_type

            # Evaluate the body.
            stack.push(Frame(body, env))

            frame.expression_index = 2
            return None

        else:
            # We've evaluated the body without any errors, just return
            # the result.
            return frame.evalled[-1]


# TODO: rethrow, to throw an exception but with the stacktrace from
# the original call site.
class Throw(Function):
    def call(self, args):
        check_args(u'throw', args, 2, 2)

        exception_type = args[0]
        exception_message = args[1]

        if not isinstance(exception_type, TrifleExceptionType):
            return TrifleExceptionInstance(
                wrong_type,
                u"The first argument to throw must be an exception type, but got: %s"
                % exception_type.repr())

        if not isinstance(exception_message, String):
            return TrifleExceptionInstance(
                wrong_type,
                u"The second argument to throw must be a string, but got: %s"
                % exception_message.repr())

        return TrifleExceptionInstance(
            exception_type,
            exception_message.as_unicode(),
        )


class Message(Function):
    def call(self, args):
        check_args(u'message', args, 1, 1)

        exception = args[0]
        
        if not isinstance(exception, TrifleExceptionInstance):
            return TrifleExceptionInstance(
                wrong_type,
                u"The first argument to message must be an exception, but got: %s"
                % exception.repr())

        return String(list(exception.message))


class ExceptionType(Function):
    def call(self, args):
        check_args(u'exception-type', args, 1, 1)

        exception = args[0]
        
        if not isinstance(exception, TrifleExceptionInstance):
            return TrifleExceptionInstance(
                wrong_type,
                u"The first argument to function `exception-type` must be an exception, but got: %s"
                % exception.repr())

        return exception.exception_type


class Printable(Function):
    def call(self, args):
        check_args(u'printable', args, 1, 1)
        return String(list(args[0].repr()))
