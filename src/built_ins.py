from trifle_types import (Function, Lambda, Macro, Special, Integer, List,
                          Boolean, TRUE, FALSE, NULL, Symbol, Keyword)
from errors import TrifleTypeError
from almost_python import deepcopy, copy


# todo: rewrite this as a macro that calls set-symbol!
class Set(Special):
    def call(self, args, env):
        if len(args) != 2:
            # todo: print the actual arguments given
            # todo: separate error for argument number vs type
            raise TrifleTypeError(
                "set! takes 2 arguments, but got %d." % len(args))

        variable_name = args[0]
        variable_value = args[1]

        if not isinstance(variable_name, Symbol):
            raise TrifleTypeError(
                "The first argument to set! must be a symbol, but got %s."
                % variable_name.repr())

        from evaluator import evaluate
        env.set(variable_name.symbol_name, evaluate(variable_value, env))

        return NULL


# todoc
class Let(Special):
    def call(self, args, env):
        if not args:
            # todo: could we pass list elements in List's constructor?
            list_args = List()
            list_args.values = args
            
            raise TrifleTypeError(
                "let takes at least 1 argument, but got: %s" % list_args.repr())

        bindings = args[0]
        expressions = args[1:]

        # todo: it would be easier if we passed List objects around,
        # and implemented a slice method on them.
        list_expressions = List()
        list_expressions.values = expressions

        if not isinstance(bindings, List):
            raise TrifleTypeError(
                "let requires a list as its first argument, but got: %s"
                % bindings.repr()
            )

        for index, expression in enumerate(bindings.values):
            if index % 2 == 0:
                if not isinstance(expression, Symbol):
                    raise TrifleTypeError(
                        "Expected a symbol for a let-bound variable, but got: %s"
                        % expression.repr()
                    )

        if len(bindings.values) % 2 == 1:
            # todo: this should be an arity error
            raise TrifleTypeError(
                "no value given for let-bound variable: %s"
                % bindings.values[-1].repr())

        # Fix circular import by importing here.
        from evaluator import evaluate, evaluate_all
        from environment import LetScope

        # Build a scope with the let variables
        let_scope = LetScope({})
        let_env = env.with_nested_scope(let_scope)

        # Bind each symbol to the result of evaluating each
        # expression. We allow access to previous symbols in this let.
        for i in range(len(bindings.values) / 2):
            symbol = bindings.values[2 * i]
            value = evaluate(bindings.values[2 * i + 1], let_env)
            let_scope.set(symbol.symbol_name, value)

        return evaluate_all(list_expressions, let_env)


def check_parameters(parameter_list):
    """Ensure that parameter_list is a trifle list that only contains
    variables, or :rest in the correct position.

    """
    if not isinstance(parameter_list, List):
        raise TrifleTypeError(
            "Parameter lists must be lists, but got: %s" % parameter_list.repr())
    
    for index, param in enumerate(parameter_list.values):
        if isinstance(param, Symbol):
            continue

        if isinstance(param, Keyword):
            if param.symbol_name == 'rest':
                if index == len(parameter_list.values) - 2:
                    continue

        raise TrifleTypeError(
            "Invalid parameter in parameter list: %s" %
            param.repr())


class LambdaFactory(Special):
    """Return a fresh Lambda object every time it's called."""

    def call(self, args, env):
        if not args:
            # todo: separate error for argument number vs type
            raise TrifleTypeError(
                "lambda takes at least 1 argument, but got 0.")

        parameters = args[0]

        check_parameters(parameters)

        lambda_body = List()
        for arg in args[1:]:
            lambda_body.append(arg)
        
        return Lambda(parameters, lambda_body, env)


# todo: do we want to support anonymous macros, similar to lambda?
# todo: expose macro expand functions to the user
# todo: support docstrings
class DefineMacro(Special):
    """Create a new macro object and bind it to the variable name given,
    in the global scope.

    """

    def call(self, args, env):
        if len(args) < 2:
            # todo: separate error for argument number vs type
            raise TrifleTypeError(
                "macro takes at least 2 arguments, but got %d." % len(args))

        macro_name = args[0]
        parameters = args[1]
        
        if not isinstance(macro_name, Symbol):
            raise TrifleTypeError(
                "macro name should be a symbol, but got %s" %
                parameters.repr())

        parameters = args[1]
        check_parameters(parameters)

        macro_body = List()
        for arg in args[2:]:
            macro_body.append(arg)

        env.set_global(macro_name.symbol_name,
                       Macro(parameters, macro_body))

        return NULL


# todo: it would be nice to define this as a trifle macro using a quote primitive
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

        if not list_head.symbol_name == 'unquote':
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

        if not list_head.symbol_name == 'unquote*':
            return False

        return True
    
    # todo: fix the potential stack overflow
    # todo: throw errors on (unquote two arguments!) and (unquote)
    def evaluate_unquote_calls(self, expression, env):
        from evaluator import evaluate
        if isinstance(expression, List):
            for index, item in enumerate(copy(expression).values):
                if self.is_unquote(item):
                    unquote_argument = item.values[1]
                    expression.values[index] = evaluate(unquote_argument, env)
                    
                elif self.is_unquote_star(item):
                    unquote_argument = item.values[1]
                    values_list = evaluate(unquote_argument, env)

                    # todo: unit test this error
                    if not isinstance(values_list, List):
                        raise TrifleTypeError(
                            "unquote* must be used with a list, but got a %s" % values_list.repr())

                    # Splice in the result of evaluating the unquote* argument
                    expression.values = expression.values[:index] + values_list.values + expression.values[index+1:]

                elif isinstance(item, List):
                    # recurse the nested list
                    self.evaluate_unquote_calls(item, env)

        return expression
                        
    
    def call(self, args, env):
        if len(args) != 1:
            # todo: print the actual arguments given
            raise TrifleTypeError(
                "quote takes 1 argument, but got %d." % len(args))

        return self.evaluate_unquote_calls(deepcopy(args[0]), env)


class If(Special):
    def call(self, args, env):
        if len(args) not in [2, 3]:
            # todo: print the actual arguments given
            raise TrifleTypeError(
                "if takes 2 or 3 arguments, but got %d." % len(args))

        condition = args[0]
        then = args[1]

        from evaluator import evaluate
        if is_truthy(evaluate(condition, env)) == TRUE:
            return evaluate(then, env)
        else:
            if len(args) == 3:
                otherwise = args[2]
                return evaluate(otherwise, env)
            else:
                return NULL


def is_truthy(value):
    """Convert the value to the trifle values `true` or `false`
    depending on its truthiness.

    """
    if isinstance(value, Boolean):
        if value == FALSE:
            return FALSE

    if isinstance(value, Integer):
        if value.value == 0:
            return FALSE

    if isinstance(value, List):
        if len(value.values) == 0:
            return FALSE

    return TRUE

        
class Truthy(Function):
    def call(self, args):
        if len(args) != 1:
            # todoc: this error
            # todo: print the actual arguments given
            raise TrifleTypeError(
                "truthy? takes 1 argument, but got %d." % len(args))

        return is_truthy(args[0])


class While(Special):
    def call(self, args, env):
        if not args:
            raise TrifleTypeError(
                "while takes at least one argument.")

        from evaluator import evaluate
        while True:
            condition = evaluate(args[0], env)
            if is_truthy(condition) == FALSE:
                break

            for arg in args[1:]:
                evaluate(arg, env)

        return NULL


class Same(Function):
    def call(self, args):
        if len(args) != 2:
            # todo: print the actual arguments given
            raise TrifleTypeError(
                "same? takes 2 arguments, but got %d." % len(args))

        # Sadly, we can't access .__class__ in RPython.
        if isinstance(args[0], Symbol):
            if isinstance(args[1], Symbol):
                if args[0].symbol_name == args[1].symbol_name:
                    return TRUE

            return FALSE

        if isinstance(args[0], Integer):
            if isinstance(args[1], Integer):
                if args[0].value == args[1].value:
                    return TRUE

            return FALSE

        if args[0] is args[1]:
            return TRUE
        else:
            return FALSE


class FreshSymbol(Function):
    def __init__(self):
        self.count = 1

    def call(self, args):
        if args:
            args_list = List()
            args_list.values = args
            
            # todo: print the actual arguments given
            raise TrifleTypeError(
                "fresh-symbol takes 0 arguments, but got: %s" % args_list.repr())

        symbol_name = "%d-unnamed" % self.count
        self.count += 1

        return Symbol(symbol_name)


class Add(Function):
    def call(self, args):
        for arg in args:
            # todo: we will want other numeric types
            if not isinstance(arg, Integer):
                raise TrifleTypeError(
                    "+ requires numbers, but got: %s." % arg.repr())

        total = 0
        for arg in args:
            total += arg.value
        return Integer(total)


class Subtract(Function):
    def call(self, args):
        for arg in args:
            # todo: we will want other numeric types
            if not isinstance(arg, Integer):
                raise TrifleTypeError(
                    "- requires numbers, but got: %s." % arg.repr())

        if not args:
            return Integer(0)

        if len(args) == 1:
            return Integer(-args[0].value)

        total = args[0].value
        for arg in args[1:]:
            total -= arg.value
        return Integer(total)


class Multiply(Function):
    def call(self, args):
        for arg in args:
            # todo: we will want other numeric types
            if not isinstance(arg, Integer):
                raise TrifleTypeError(
                    "* requires numbers, but got: %s." % arg.repr())

        product = 1
        for arg in args:
            product *= arg.value

        return Integer(product)


class LessThan(Function):
    def call(self, args):
        if len(args) < 2:
            # todo: print the actual arguments given
            raise TrifleTypeError(
                "< takes at least 2 arguments, but got %d." % len(args))
        
        for arg in args:
            # todo: we will want other numeric types
            if not isinstance(arg, Integer):
                raise TrifleTypeError(
                    "%s is not a number." % arg.repr())

        previous_arg = args[0]
        for arg in args[1:]:
            if not previous_arg.value < arg.value:
                return FALSE

            previous_arg = arg

        return TRUE


# todo: support negative indexes
class GetIndex(Function):
    def call(self, args):
        if len(args) != 2:
            args_list = List()
            args_list.values = args
            
            raise TrifleTypeError(
                "get-index takes 2 arguments, but got: %s" % args_list.repr())

        some_list = args[0]
        index = args[1]

        if not isinstance(some_list, List):
            raise TrifleTypeError(
                "the first argument to get-index must be a list, but got: %s"
                % some_list.repr())

        if not isinstance(index, Integer):
            raise TrifleTypeError(
                "the second argument to get-index must be an integer, but got: %s"
                % index.repr())

        # todo: separate error class
        if index.value < 0 or index.value >= len(some_list.values):
            raise TrifleTypeError(
                "the list has %d items, but you asked for index %d"
                % (len(some_list.values), index.value))

        return some_list.values[index.value]


class Length(Function):
    def call(self, args):
        if len(args) != 1:
            args_list = List()
            args_list.values = args
            
            raise TrifleTypeError(
                "length takes 1 argument, but got: %s" % args_list.repr())

        some_list = args[0]

        if not isinstance(some_list, List):
            raise TrifleTypeError(
                "the first argument to length must be a list, but got: %s"
                % some_list.repr())

        return Integer(len(some_list.values))


# todo: support negative indexes
class SetIndex(Function):
    def call(self, args):
        if len(args) != 3:
            args_list = List()
            args_list.values = args
            
            raise TrifleTypeError(
                "set-index! takes 3 arguments, but got: %s" % args_list.repr())

        some_list = args[0]
        index = args[1]
        value = args[2]

        if not isinstance(some_list, List):
            raise TrifleTypeError(
                "the first argument to set-index! must be a list, but got: %s"
                % some_list.repr())

        if not isinstance(index, Integer):
            raise TrifleTypeError(
                "the second argument to set-index! must be an integer, but got: %s"
                % index.repr())

        # todo: separate error class
        if index.value < 0 or index.value >= len(some_list.values):
            raise TrifleTypeError(
                "the list has %d items, but you tried to set index %d"
                % (len(some_list.values), index.value))

        some_list.values[index.value] = value

        return NULL


class Append(Function):
    def call(self, args):
        if len(args) != 2:
            args_list = List()
            args_list.values = args
            
            raise TrifleTypeError(
                "append! takes 2 arguments, but got: %s" % args_list.repr())

        some_list = args[0]
        value = args[1]

        if not isinstance(some_list, List):
            raise TrifleTypeError(
                "the first argument to append! must be a list, but got: %s"
                % some_list.repr())

        some_list.values.append(value)

        return NULL


# todo: replace with a prelude function that uses append!
class Push(Function):
    def call(self, args):
        if len(args) not in [2, 3]:
            args_list = List()
            args_list.values = args
            
            raise TrifleTypeError(
                "push! takes 2 or 3 arguments, but got: %s" % args_list.repr())

        some_list = args[0]
        value = args[1]

        if not isinstance(some_list, List):
            raise TrifleTypeError(
                "the first argument to push! must be a list, but got: %s"
                % some_list.repr())

        index = 0
        if len(args) == 3:
            specified_index = args[2]

            if not isinstance(specified_index, Integer):
                raise TrifleTypeError(
                    "the third argument to push! must be an integer, but got: %s"
                    % specified_index.repr())
                
            # todo: separate error class for index errors
            if specified_index.value < 0 or specified_index.value > len(some_list.values):
                raise TrifleTypeError(
                    "the list has %d items, but you tried to push at index %d"
                    % (len(some_list.values), specified_index.value))

            index = specified_index.value

        # This if test is redundant, but it keeps RPython happy since
        # it cannot prove that index is non-negative otherwise.
        # todo: find a way to remove it but still compile
        if index >= 0:
            some_list.values.insert(index, value)

        return NULL
