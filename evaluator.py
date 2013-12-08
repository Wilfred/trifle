from trifle_types import List, Symbol, Integer, Function, Boolean
from errors import UnboundVariable, TrifleTypeError
from built_ins import Addition, Subtraction, Same


def evaluate_with_built_ins(expression):
    built_ins = {
        '+': Addition(),
        '-': Subtraction(),
        'same?': Same(),
    }
    return evaluate(expression, built_ins)


def evaluate(expression, environment):
    if isinstance(expression, List):
        return evaluate_list(expression, environment)
    else:
        return evaluate_value(expression, environment)


# todo: error on evaluating an empty list
def evaluate_list(node, environment):
    raw_list_elements = node.values

    # todo: handle forms where we don't evaluate their arguments
    list_elements = [
        evaluate(el, environment) for el in raw_list_elements]
    
    function = list_elements[0]
    arguments = list_elements[1:]

    if isinstance(function, Function):
        return function.call(arguments)
    else:
        # todoc: this error
        raise TrifleTypeError("%s isn't a function." % function.repr())


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
    elif isinstance(value, Symbol):
        symbol_name = value.symbol_name
        if symbol_name in environment:
            return environment[symbol_name]
        else:
            raise UnboundVariable("No such variable defined: '%s'"
                                  % symbol_name)
    else:
        assert False, "I don't know how to evaluate that value."
