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


class LambdaFactory(Special):
    """Return a fresh Lambda object every time it's called."""

    def call(self, args, env):
        if not args:
            # todo: separate error for argument number vs type
            raise TrifleTypeError(
                "lambda takes at least 1 argument, but got 0.")

        parameters = args[0]
        if not isinstance(parameters, List):
            raise TrifleTypeError(
                "The first argument to lambda should be a list, but got %s" %
                parameters.repr())

        for index, param in enumerate(parameters.values):
            if isinstance(param, Symbol):
                continue

            if isinstance(param, Keyword):
                if param.symbol_name == 'rest':
                    if index == len(parameters.values) - 2:
                        continue

            raise TrifleTypeError(
                "Invalid parameter specified for lambda: %s" %
                param.repr())

        lambda_body = List()
        for arg in args[1:]:
            lambda_body.append(arg)
        
        return Lambda(parameters, lambda_body, env)


# todo: unit test
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
        if not isinstance(parameters, List):
            raise TrifleTypeError(
                "macro parameters should be a list, but got %s" %
                parameters.repr())

        for param in parameters.values:
            if not isinstance(param, Symbol):
                raise TrifleTypeError(
                    "The list of parameters to macro must only contain symbols, but got %s" %
                    param.repr())

        macro_body = List()
        for arg in args[2:]:
            macro_body.append(arg)

        env.set_global(macro_name.symbol_name,
                       Macro(parameters, macro_body))

        return NULL


class Do(Function):
    def call(self, args):
        if args:
            return args[-1]
        else:
            return NULL


# todo: it would be nice to define this as a trifle macro using a quote primitive
# (e.g. elisp defines backquote in terms of quote)
# todoc: unquote, unquote*
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
        expression = deepcopy(expression)

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

        return self.evaluate_unquote_calls(args[0], env)


class If(Special):
    def call(self, args, env):
        if len(args) not in [2, 3]:
            # todo: print the actual arguments given
            raise TrifleTypeError(
                "if takes 2 or 3 arguments, but got %d." % len(args))

        from evaluator import evaluate
        if is_truthy(args[0]) == TRUE:
            return evaluate(args[1], env)
        else:
            if len(args) == 3:
                return evaluate(args[2], env)
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


class Addition(Function):
    def call(self, args):
        for arg in args:
            # todo: we will want other numeric types
            if not isinstance(arg, Integer):
                raise TrifleTypeError(
                    "%s is not a number." % arg.repr())

        total = 0
        for arg in args:
            total += arg.value
        return Integer(total)


class Subtraction(Function):
    def call(self, args):
        for arg in args:
            # todo: we will want other numeric types
            if not isinstance(arg, Integer):
                raise TrifleTypeError(
                    "%s is not a number." % arg.repr())

        if not args:
            return Integer(0)

        if len(args) == 1:
            return Integer(-args[0].value)

        total = args[0].value
        for arg in args[1:]:
            total -= arg.value
        return Integer(total)


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
