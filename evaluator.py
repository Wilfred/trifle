from trifle_types import (List, Symbol, Integer, Null, NULL,
                          Function, Lambda, Macro, Special, Boolean)
from errors import UnboundVariable, TrifleTypeError
from environment import fresh_environment
from almost_python import zip


def evaluate_all_with_built_ins(expressions):
    """Evaluate a trfle List of expressions, starting with a fresh environment
    containing only the built-in functions, special expressions and macros.

    """
    return evaluate_all(expressions, fresh_environment())


# todo: remove this, it's only used in tests
def evaluate_with_built_ins(expression):
    return evaluate(expression, fresh_environment())


def evaluate_all(expressions, environment):
    """Evaluate a trifle List of expressions, starting with a fresh environment
    containing only the built-in functions, special expressions and macros.

    """
    result = NULL
    
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
    elif isinstance(function, Special):
        return function.call(raw_arguments, environment)

    elif isinstance(function, Lambda):
        # First, evaluate the arguments to this lambda.
        arguments = [
            evaluate(el, environment) for el in raw_arguments]

        # Ensure we have the right number of arguments:
        # TODO: optional and variable arguments
        if len(arguments) != len(function.arguments.values):
            # todo: unit test this error
            # todo: we should try to find a name for lambda functions,
            # or at least say where they were defined
            raise TrifleTypeError("lambda expression takes %d arguments, but got %d" %
                                  (len(function.arguments.values), len(arguments)))

        # Build a new environment to evaluate with.
        inner_scope = {}
        for variable, value in zip(function.arguments.values, arguments):
            inner_scope[variable.symbol_name] = value

        lambda_env = function.env.with_nested_scope(inner_scope)

        # Evaluate the lambda's body in our new environment.
        return evaluate_all(function.body, lambda_env)
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
        if environment.contains(symbol_name):
            return environment.get(symbol_name)
        else:
            raise UnboundVariable("No such variable defined: '%s'"
                                  % symbol_name)
    else:
        assert False, "I don't know how to evaluate that value."
