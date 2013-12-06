from parser import Node, Leaf
from trifle_types import Symbol, Integer
from errors import UnboundVariable


def evaluate(expression, environment):
    if isinstance(expression, Node):
        return evaluate_list(expression, environment)
    else:
        return evaluate_value(expression, environment)


# todo: error if we try to call something that isn't a lambda or built-in function
# todo: error on evaluating an empty list
# todoc: we evaluate functions left-to-right
def evaluate_list(node, environment):
    list_elements = node.values
    function = list_elements[0]
    raw_arguments = list_elements[1:]

    if isinstance(function, Leaf) and \
       isinstance(function.value, Symbol):
        if function.value.symbol_name == "+":
            # evaluate arguments.
            # todo: a generic way of specifying forms where we need to evaluate their arguments.
            # todo: we should only pass the global env here
            arguments = [evaluate(arg, environment) for arg in raw_arguments]

            # todo: we will eventually need to check that all arguments
            # are numbers, but we don't support any other types yet.
            total = 0
            for argument in arguments:
                total += argument.value
            return Integer(total)
            
    assert False, "I don't know how to evaluate that."


def evaluate_value(leaf, environment):
    raw_value = leaf.value
    if isinstance(raw_value, Integer):
        # Integers evaluate to themselves
        return raw_value
    if isinstance(raw_value, Symbol):
        symbol_name = raw_value.symbol_name
        if symbol_name in environment:
            return environment[symbol_name]
        else:
            raise UnboundVariable("No such variable defined: '%s'"
                                  % symbol_name)
            # todo: proper error handling
            assert False, "Unbound variable"
    else:
        assert False, "I don't know how to evaluate that value."
