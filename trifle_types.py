"""Note that 'types' is part of the python standard library, so we're
forced to name this file trifle_types.

RPython ignores magic methods (except __init__) but we implement them
for convenience when testing.

"""

class TrifleType(object):
    def __repr__(self):
        """We can't override __repr__ in rpython, so this is only useful when
        debugging with CPython.

        """
        return "<%s: %s>" % (self.__class__.__name__, self.repr())


class Boolean(TrifleType):
    def repr(self):
        if self.value:
            return "true"
        else:
            return "false"

    def __eq__(self, other):
        if self.__class__ != other.__class__:
            return False

        return self.value == other.value

    def __init__(self, value):
        self.value = value


TRUE = Boolean(True)


FALSE = Boolean(False)


class Integer(TrifleType):
    def repr(self):
        return "%s" % self.value

    def __eq__(self, other):
        if self.__class__ != other.__class__:
            return False

        return self.value == other.value

    def __init__(self, value):
        self.value = value


class Symbol(TrifleType):
    def repr(self):
        return self.symbol_name

    def __repr__(self):
        return "<%s: %s>" % (self.__class__.__name__, self.symbol_name)

    def __eq__(self, other):
        if self.__class__ != other.__class__:
            return False

        return self.symbol_name == other.symbol_name

    def __init__(self, symbol_name):
        self.symbol_name = symbol_name


class Function(TrifleType):
    """A function provided by the interpreter. Subclasses must provide a
    call method. Arguments are passed in after being evaluated.

    """
    def repr(self):
        # todo: we can be more helpful than this
        return "<function>"


"""Our parenthesis classes aren't exposed to the user, but we add them
for consistency when boxing values from the lexer.

"""

class OpenParen(TrifleType):
    pass


class CloseParen(TrifleType):
    pass
