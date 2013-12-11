from trifle_types import (Function, Macro, Integer, List,
                          Boolean, TRUE, FALSE, NULL, Symbol)
from errors import TrifleTypeError


# todo: rewrite this as a macro that calls set-symbol!
class Set(Macro):
    def call(self, args, env):
        if len(args) != 2:
            # todoc: this error
            # todo: print the actual arguments given
            # todo: unit test error
            # todo: separate error for argument number vs type
            raise TrifleTypeError(
                "set! takes 2 arguments, but got %d." % len(args))

        variable_name = args[0]
        variable_value = args[1]

        if not isinstance(variable_name, Symbol):
            # todoc: this error
            raise TrifleTypeError(
                "The first argument to set! must be a symbol, but got %s."
                % variable_name.repr())

        from evaluator import evaluate
        env[variable_name.symbol_name] = evaluate(variable_value, env)

        return NULL


# todoc: what it does, and the return value
class Do(Function):
    def call(self, args):
        if args:
            return args[-1]
        else:
            return NULL


class Quote(Macro):
    def call(self, args, env):
        if len(args) != 1:
            # todoc: this error
            # todo: print the actual arguments given
            # todo: unit test error
            raise TrifleTypeError(
                "quote takes 1 argument, but got %d." % len(args))

        return args[0]


class If(Macro):
    def call(self, args, env):
        if len(args) not in [2, 3]:
            # todoc: this error
            # todo: print the actual arguments given
            # todo: unit test error
            raise TrifleTypeError(
                "if takes 2 or 3 arguments, but got %d." % len(args))

        from evaluator import evaluate
        if Truthy().call([args[0]]) == TRUE:
            return evaluate(args[1], env)
        else:
            if len(args) == 3:
                return evaluate(args[2], env)
            else:
                return NULL

        
class Truthy(Function):
    def call(self, args):
        if len(args) != 1:
            # todoc: this error
            # todo: print the actual arguments given
            # todo: unit test error
            raise TrifleTypeError(
                "truthy? takes 1 arguments, but got %d." % len(args))

        if isinstance(args[0], Boolean):
            if args[0] == FALSE:
                return FALSE

        if isinstance(args[0], Integer):
            if args[0].value == 0:
                return FALSE

        if isinstance(args[0], List):
            if len(args[0].values) == 0:
                return FALSE

        return TRUE


class Same(Function):
    def call(self, args):
        if len(args) != 2:
            # todoc: this error
            # todo: print the actual arguments given
            # todo: unit test error
            raise TrifleTypeError(
                "same? takes 2 arguments, but got %d." % len(args))

        # Sadly, we can't access .__class__ in RPython.
        if isinstance(args[0], Boolean):
            if isinstance(args[1], Boolean):
                if args[0].value == args[1].value:
                    return TRUE

        if isinstance(args[0], Integer):
            if isinstance(args[1], Integer):
                if args[0].value == args[1].value:
                    return TRUE

        return FALSE


class Addition(Function):
    def call(self, args):
        for arg in args:
            # todo: we will want other numeric types
            if not isinstance(arg, Integer):
                # todoc: this error
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
                # todoc: this error
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


def fresh_environment():
    """Return a new environment that only contains the built-ins.

    """
    return {
        '+': Addition(),
        '-': Subtraction(),
        'same?': Same(),
        'truthy?': Truthy(),
        'quote': Quote(),
        'set!': Set(),
        'do': Do(),
        'if': If(),
    }
