from trifle_types import List, Symbol, Keyword
from errors import TrifleTypeError, ArityError


def validate_parameters(parameter_list):
    """Ensure that parameter_list is a trifle list that only contains
    variables, or :rest in the correct position.

    """
    if not isinstance(parameter_list, List):
        raise TrifleTypeError(
            "Parameter lists must be lists, but got: %s" % parameter_list.repr())
    
    for index, param in enumerate(parameter_list.values):
        if isinstance(param, Symbol):
            continue

        if isinstance(param, Keyword):
            if param.symbol_name == 'rest':
                if index == len(parameter_list.values) - 2:
                    continue

        raise TrifleTypeError(
            "Invalid parameter in parameter list: %s" %
            param.repr())


def is_variable_arity(parameter_list):
    if len(parameter_list.values) < 2:
        return False

    penultimate_param = parameter_list.values[-2]
    if isinstance(penultimate_param, Keyword):
        if penultimate_param.symbol_name == 'rest':
            return True

    return False


# todo: optional arguments (due to default values), keyword arguments
def check_parameters(parameter_list, given_args):
    """Ensure that we have been given sufficient arguments for this
    parameter list.

    """
    if is_variable_arity(parameter_list):
        minimum_args = len(parameter_list.values) - 2
        if len(given_args.values) < minimum_args:
            # todo: can we say *what* was expecting these arguments?
            raise ArityError("Expected at least %d argument%s, but got %d." %
                             (minimum_args,
                              "s" if minimum_args > 1 else "",
                              len(given_args.values)))
    else:
        if len(parameter_list.values) != len(given_args.values):
            raise ArityError("Expected %d argument%s, but got %d." %
                             (len(parameter_list.values),
                              "s" if len(parameter_list.values) > 1 else "",
                              len(given_args.values)))
