from built_ins import (Addition, Subtraction, LessThan, Same, Truthy,
                       Quote, Set, Do, If, While, LambdaFactory)


class Environment(object):
    """All variable bindings are stored in an environment. It handles
    nested scope by using a list of dicts, where the first dict is for
    globals and so on.

    """
    
    def __init__(self, scopes):
        self.scopes = scopes

    # we can't use __get__ and __set__ in RPython, so we use normal methods
    def get(self, variable_name):
        # Note this raises KeyError if the variable name is not
        # present, unlike .get on dict objects.

        # We search scopes starting at the innermost.
        for scope in reversed(self.scopes):
            if variable_name in scope:
                return scope[variable_name]

        raise KeyError("Could not find '%s' in environment" % variable_name)

    # todo: should use outer scopes, if the variable is already defined
    def set(self, variable_name, value):
        self.scopes[-1][variable_name] = value

    def contains(self, variable_name):
        for scope in reversed(self.scopes):
            if variable_name in scope:
                return True

        return False

    def with_nested_scope(self, inner_scope):
        """Return a new environment that shares all the outer scopes with this
        environment, but has an additional inner scope.

        """
        return Environment(self.scopes + [inner_scope])


def fresh_environment():
    """Return a new environment that only contains the built-ins.

    """
    return Environment([{
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
        'lambda': LambdaFactory(),
    }])
