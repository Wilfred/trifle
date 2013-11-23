"""Note that types in the python standard library, so we're forced to
name this file trifle_types.

RPython ignores magic methods (except __init__) but we implement them
for convenience when testing.

"""

class TrifleType(object):
    pass


class Integer(TrifleType):
    def __repr__(self):
        return "<%s: %s>" % (self.__class__.__name__, self.value)

    def __eq__(self, other):
        if self.__class__ != other.__class__:
            return False

        return self.value == other.value

    def __init__(self, value):
        self.value = value


class Symbol(TrifleType):
    def __repr__(self):
        return "<%s: %s>" % (self.__class__.__name__, self.symbol_name)

    def __eq__(self, other):
        if self.__class__ != other.__class__:
            return False

        return self.symbol_name == other.symbol_name

    def __init__(self, symbol_name):
        self.symbol_name = symbol_name


"""Our parenthesis classes aren't exposed to the user, but we add them
for consistency when boxing values from the lexer.

"""

class OpenParen(TrifleType):
    pass


class CloseParen(TrifleType):
    pass
