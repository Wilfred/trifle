from built_ins import (Addition, Subtraction, LessThan, Same, Truthy,
                       Quote, Set, Do, If, While)


class Environment(object):
    """All variable bindings are stored in an environment. It handles
    nested scope by using a list of dicts, where the first dict is for
    globals and so on.

    """
    
    def __init__(self, initial):
        self.scopes = [initial]

    # we can't use __get__ and __set__ in RPython, so we use normal methods
    def get(self, variable_name):
        # Note this raises KeyError if the variable name is not
        # present, unlike .get on dict objects.
        return self.scopes[0][variable_name]

    def set(self, variable_name, value):
        self.scopes[0][variable_name] = value

    def contains(self, variable_name):
        return variable_name in self.scopes[0]


def fresh_environment():
    """Return a new environment that only contains the built-ins.

    """
    return Environment({
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
    })
