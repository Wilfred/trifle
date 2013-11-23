"""Note that types in the python standard library, so we're forced to
name this file baobab_types.

"""

class BaobabType(object):
    def __eq__(self, other):
        if self.__class__ != other.__class__:
            return False

        return self.value == other.value

    def __repr__(self):
        return "<%s: %s>" % (self.__class__.__name__, self.value)


class Integer(BaobabType):
    def __init__(self, value_as_string):
        self.value = int(value_as_string)


class Symbol(BaobabType):
    def __init__(self, value_as_string):
        self.value = value_as_string

"""Our parenthesis classes aren't exposed to the user, but we add them
for consistency when boxing values from the lexer.

"""

class OpenParen(BaobabType):
    pass


class CloseParen(BaobabType):
    pass
