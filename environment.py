from built_ins import (Addition, Subtraction, LessThan, Same, Truthy,
                       Quote, Set, Do, If, While)

def fresh_environment():
    """Return a new environment that only contains the built-ins.

    """
    return {
        '+': Addition(),
        '-': Subtraction(),
        '<': LessThan(),
        'same?': Same(),
        'truthy?': Truthy(),
        'quote': Quote(),
        'set!': Set(),
        'do': Do(),
        'if': If(),
        'while': While(),
    }
