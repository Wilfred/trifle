from trifle_types import List, Symbol, Integer, Function, Macro, Boolean
from errors import UnboundVariable, TrifleTypeError
from built_ins import Addition, Subtraction, Same, Quote, Do


def evaluate_with_built_ins(expression):
    built_ins = {
        '+': Addition(),
        '-': Subtraction(),
        'same?': Same(),
        'quote': Quote(),
        'do': Do(),
    }
    return evaluate(expression, built_ins)


def evaluate(expression, environment):
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
    if isinstance(value, Boolean):
        # Booleans evaluate to themselves
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
