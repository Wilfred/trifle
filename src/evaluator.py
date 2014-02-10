from trifle_types import (List, Bytes, Symbol,
                          Integer, Float,
                          Null, NULL,
                          Function, FunctionWithEnv, Lambda, Macro, Special, Boolean,
                          Keyword, String)
from errors import UnboundVariable, TrifleTypeError
from almost_python import zip
from environment import Scope
from parameters import is_variable_arity, check_parameters


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


# todo: this would be simpler if `values` was also a trifle List
def build_scope(parameters, values):
    """Build a single scope where every value in values (a python list) is
    bound to a symbol according to the parameters List given.

    If the parameters list contains `:rest foo`, any remaining arguments
    are passed a list in the named parameter.

    """
    varargs = is_variable_arity(parameters)

    if varargs:
        # The only negative slice supported by RPython is -1, so we
        # have to do it twice.
        normal_parameters = parameters.values[:-1][:-1]
    else:
        normal_parameters = parameters.values

    # Ensure we have the right number of arguments:
    check_parameters(parameters, List(values))

    scope = Scope({})
    for variable, value in zip(normal_parameters, values):
        scope.set(variable.symbol_name,  value)

    # todoc: varargs on macros
    # todo: consistently use the terms 'parameters' and 'arguments'
    if varargs:
        # Create a Trifle list of any remaining arguments.
        remaining_args = List(values[len(normal_parameters):])

        # Assign it to the variable args symbol.
        scope.set(parameters.values[-1].symbol_name, remaining_args)

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
        
    if isinstance(function, FunctionWithEnv):
        arguments = [
            evaluate(el, environment) for el in raw_arguments]
        return function.call(arguments, environment)
        
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
        raise TrifleTypeError(u"%s isn't a function or macro."
                              % function.repr())


def evaluate_value(value, environment):
    if isinstance(value, Integer):
        # Integers evaluate to themselves
        return value
    elif isinstance(value, Float):
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
    elif isinstance(value, String):
        # Strings evaluate to themselves
        return value
    elif isinstance(value, Bytes):
        # Strings evaluate to themselves
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
            raise UnboundVariable(u"No such variable defined: '%s'"
                                  % symbol_name)
    else:
        assert False, "I don't know how to evaluate that value."
