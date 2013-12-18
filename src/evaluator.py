from trifle_types import (List, Symbol, Integer, Null, NULL,
                          Function, Lambda, Macro, Special, Boolean,
                          Keyword)
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


def build_scope(parameters, values):
    """Build a single scope where every value in values (a python list) is
    bound to a symbol according to the parameters List given.

    If the parameters list contains `:rest foo`, any remaining arguments
    are passed a list in the named parameter.

    """
    varargs = False
    if len(parameters.values) >= 2:
        if isinstance(parameters.values[-2], Keyword) and \
           parameters.values[-2].symbol_name == 'rest':
            varargs = True

    if varargs:
        normal_parameters = parameters.values[:-2]
    else:
        normal_parameters = parameters.values
    
    # Ensure we have the right number of arguments:
    # TODO: optional arguments
    if len(normal_parameters) > len(values):
        # todo: unit test this error for both lambda and macros
        # todo: say what parameters we expected
        if varargs:
            raise TrifleTypeError("expected at least %d arguments, but got %d" %
                                  (len(normal_parameters), len(values)))
        else:
            raise TrifleTypeError("expected %d arguments, but got %d" %
                                  (len(normal_parameters), len(values)))

    scope = {}
    for variable, value in zip(normal_parameters, values):
        scope[variable.symbol_name] = value

    # todoc: varargs on macros
    # todo: consistently use the terms 'parameters' and 'arguments'
    if varargs:
        # Create a Trifle list of any remaining arguments.
        remaining_args = List()
        remaining_args.values = values[len(normal_parameters):]

        # Assign it to the variable args symbol.
        scope[parameters.values[-1].symbol_name] = remaining_args

    return scope


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
        # Build a new environment to evaluate with.
        inner_scope = build_scope(function.arguments, raw_arguments)

        macro_env = environment.globals_only().with_nested_scope(inner_scope)

        # Evaluate the macro body, returning an expression
        expression = evaluate_all(function.body, macro_env)

        # Evaluate the expanded expression
        return evaluate(expression, environment)

    elif isinstance(function, Special):
        return function.call(raw_arguments, environment)

    elif isinstance(function, Lambda):
        # First, evaluate the arguments to this lambda.
        arguments = [
            evaluate(el, environment) for el in raw_arguments]

        # Build a new environment to evaluate with.
        inner_scope = build_scope(function.arguments, arguments)

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
    elif isinstance(value, Keyword):
        # Keywords evaluate to themselves
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
