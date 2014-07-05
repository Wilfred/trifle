from trifle_types import List, Symbol, Keyword, TrifleExceptionInstance
from errors import ArityError, wrong_type, value_error


def validate_parameters(parameter_list):
    """Ensure that parameter_list is a trifle list that only contains
    variables, or :rest in the correct position.

    """
    if not isinstance(parameter_list, List):
        return TrifleExceptionInstance(
            wrong_type,
            u"Parameter lists must be lists, but got: %s"
            % parameter_list.repr())

    # Poor man's set: RPython doesn't support proper sets:
    # http://stackoverflow.com/q/4741058
    seen_symbols = {}
    
    for index, param in enumerate(parameter_list.values):
        if isinstance(param, Symbol):

            if param.symbol_name in seen_symbols:
                return TrifleExceptionInstance(
                    value_error,
                    u"Repeated parameter in parameter list: %s" %
                    param.repr())
            else:
                seen_symbols[param.symbol_name] = True
                continue

        if isinstance(param, Keyword):
            if param.symbol_name == u'rest':
                if index == len(parameter_list.values) - 2:
                    continue

        return TrifleExceptionInstance(
            wrong_type,
            u"Invalid parameter in parameter list: %s" %
            param.repr())


def is_variable_arity(parameter_list):
    if len(parameter_list.values) < 2:
        return False

    penultimate_param = parameter_list.values[-2]
    if isinstance(penultimate_param, Keyword):
        if penultimate_param.symbol_name == u'rest':
            return True

    return False


# todo: optional arguments (due to default values), keyword arguments
def check_parameters(name, parameter_list, given_args):
    """Ensure that we have been given sufficient arguments for this
    parameter list.

    """
    if is_variable_arity(parameter_list):
        minimum_args = len(parameter_list.values) - 2
        if len(given_args.values) < minimum_args:
            # todo: can we say *what* was expecting these arguments?
            raise ArityError(u"%s expected at least %d argument%s, but got %d." %
                             (name, minimum_args,
                              u"s" if minimum_args > 1 else u"",
                              len(given_args.values)))
    else:
        if len(parameter_list.values) != len(given_args.values):
            raise ArityError(u"Expected %d argument%s, but got %d." %
                             (len(parameter_list.values),
                              u"s" if len(parameter_list.values) > 1 else u"",
                              len(given_args.values)))
