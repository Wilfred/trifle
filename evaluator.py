from parser import Node, Leaf
from trifle_types import Symbol, Integer


# todo: define an environment
def evaluate(expression):
    if isinstance(expression, Node):
        return evaluate_list(expression)
    else:
        return evaluate_value(expression)


# todo: lookup functions in an environment
# todo: error if we try to call something that isn't a lambda or built-in function
# todo: error on evaluating an empty list
# todoc: we evaluate functions left-to-right
def evaluate_list(node):
    list_elements = node.values
    function = list_elements[0]
    raw_arguments = list_elements[1:]

    if isinstance(function, Leaf) and \
       isinstance(function.value, Symbol) and \
       function.value.symbol_name == "+":
        # evaluate arguments.
        # todo: always do this, even if we're not calling +
        arguments = [evaluate(arg) for arg in raw_arguments]

        # todo: we will eventually need to check that all arguments
        # are numbers, but we don't support any other types yet.
        total = 0
        for argument in arguments:
            total += argument.value
        return Integer(total)
    else:
        assert False, "Can only evaluate calls to +"


def evaluate_value(leaf):
    raw_value = leaf.value
    if isinstance(raw_value, Integer):
        # Integers evaluate to themselves
        return raw_value
    else:
        assert False, "Can't evaluate symbols yet."
