from trifle_types import List, Symbol, Keyword
from errors import TrifleTypeError


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


