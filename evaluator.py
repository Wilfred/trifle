from trifle_types import (List, Symbol, Integer, Null,
                          Function, Macro, Boolean)
from errors import UnboundVariable, TrifleTypeError
from environment import fresh_environment


def evaluate_all_with_built_ins(expressions):
    """Evaluate a trfle List of expressions, starting with a fresh environment
    containing only the built-in functions and macros.

    """
    return evaluate_all(expressions, fresh_environment())


# todo: remove this, it's only used in tests
def evaluate_with_built_ins(expression):
    return evaluate(expression, fresh_environment())


def evaluate_all(expressions, environment):
    """Evaluate a trfle List of expressions, starting with a fresh environment
    containing only the built-in functions and macros.

    """
    # todo: null instead
    result = Integer(0)
    
    for expression in expressions.values:
        result = evaluate(expression, environment)

    return result


def evaluate(expression, environment):
    """Evaluate the given expression in the given environment.

    """
    if isinstance(expression, List):
        return evaluate_list(expression, environment)
    else:
        return evaluate_value(expression, environment)


# todo: error on evaluating an empty list
def evaluate_list(node, environment):
    list_elements = node.values
    function = evaluate(list_elements[0], environment)
    raw_arguments = list_elements[1:]

    if isinstance(function, Function):
        arguments = [
            evaluate(el, environment) for el in raw_arguments]
        return function.call(arguments)
    elif isinstance(function, Macro):
        return function.call(raw_arguments, environment)
    else:
        # todoc: this error
        raise TrifleTypeError("%s isn't a function or macro."
                              % function.repr())


def evaluate_value(value, environment):
    if isinstance(value, Integer):
        # Integers evaluate to themselves
        return value
    elif isinstance(value, Boolean):
        # Booleans evaluate to themselves
        return value
    elif isinstance(value, Null):
        # Null evaluates to itself
        return value
    elif isinstance(value, Function):
        # Functions evaluate to themselves
        return value
    elif isinstance(value, Macro):
        # Macros evaluate to themselves
        return value
    elif isinstance(value, Symbol):
        symbol_name = value.symbol_name
        if symbol_name in environment:
            return environment[symbol_name]
        else:
            raise UnboundVariable("No such variable defined: '%s'"
                                  % symbol_name)
    else:
        assert False, "I don't know how to evaluate that value."
