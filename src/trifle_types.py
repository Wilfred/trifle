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


# TODO: move to a consistent naming scheme: .boolean_value, .list_value etc.
class Boolean(TrifleType):
    def repr(self):
        if self.value:
            return u"#true"
        else:
            return u"#false"

    def __eq__(self, other):
        """We deliberately treat Integer(1) as different to Float(1.0) since
        this magic method is only used in tests and it avoids confusion.

        """
        if self.__class__ != other.__class__:
            return False

        return self.value == other.value

    def __init__(self, value):
        self.value = value


TRUE = Boolean(True)


FALSE = Boolean(False)


class Null(TrifleType):
    def repr(self):
        return u"#null"


NULL = Null()


class Integer(TrifleType):
    def repr(self):
        return u"%d" % self.value

    def __eq__(self, other):
        if self.__class__ != other.__class__:
            return False

        return self.value == other.value

    def __init__(self, value):
        assert isinstance(value, int)
        self.value = value


class Float(TrifleType):
    def repr(self):
        return u"%f" % self.float_value

    def __eq__(self, other):
        if self.__class__ != other.__class__:
            return False

        return self.float_value == other.float_value

    def __init__(self, value):
        assert isinstance(value, float)
        self.float_value = value


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
        assert isinstance(symbol_name, unicode)
        self.symbol_name = symbol_name


# TODOC
class Keyword(TrifleType):
    def repr(self):
        return u":%s" % self.symbol_name

    def __repr__(self):
        return "<%s: %s>" % (self.__class__.__name__, self.symbol_name)

    def __eq__(self, other):
        if self.__class__ != other.__class__:
            return False

        return self.symbol_name == other.symbol_name

    def __init__(self, symbol_name):
        assert isinstance(symbol_name, unicode)
        self.symbol_name = symbol_name


class Character(TrifleType):
    def repr(self):
        if self.character == '\n':
            return u"'\\n'"
        elif self.character == "'":
            return u"'\\''"
        elif self.character == "\\":
            return u"'\\\\'"
        else:
            return u"'%s'" % self.character

    def __repr__(self):
        return "<%s: %s>" % (self.__class__.__name__, self.character)

    def __eq__(self, other):
        if self.__class__ != other.__class__:
            return False

        return self.character == other.character

    def __init__(self, character):
        assert isinstance(character, unicode)
        assert len(character) == 1

        self.character = character


class String(TrifleType):
    def repr(self):
        return u'"%s"' % self.as_unicode()

    def __repr__(self):
        return "<%s: %s>" % (self.__class__.__name__, self.string)

    def __eq__(self, other):
        if self.__class__ != other.__class__:
            return False

        return self.string == other.string

    def as_unicode(self):
        return u"".join(self.string)

    def __init__(self, string):
        """We expect a list of unicode chars."""
        assert isinstance(string, list)
        if string:
            assert isinstance(string[0], unicode)

        self.string = string


class List(TrifleType):
    def __init__(self, values=None):
        if values is None:
            self.values = []
        else:
            assert isinstance(values, list)
            self.values = values

    def append(self, value):
        self.values.append(value)

    # todo: fix infinite loop for lists that contain themselves
    def repr(self):
        element_reprs = [element.repr() for element in self.values]
        return u"(%s)" % u" ".join(element_reprs)

    def __eq__(self, other):
        if not isinstance(other, List):
            return False
        else:
            return self.values == other.values


class Bytestring(TrifleType):
    def __init__(self, byte_value):
        assert isinstance(byte_value, bytearray)
        self.byte_value = byte_value

    def __eq__(self, other):
        if self.__class__ != other.__class__:
            return False

        return self.byte_value == other.byte_value

    def repr(self):
        SMALLEST_PRINTABLE_CHAR = ' '
        LARGEST_PRINTABLE_CHAR = '~'

        printable_chars = []

        for char in str(self.byte_value):
            if SMALLEST_PRINTABLE_CHAR <= char <= LARGEST_PRINTABLE_CHAR:
                if char == "\\":
                    printable_chars.append("\\\\")
                else:
                    printable_chars.append(char)
            else:
                # e.g. "0x21"
                hexadecimal = hex(ord(char))
                printable_chars.append("\\x%s" % hexadecimal[2:])

        return u'#bytes("%s")' % ("".join(printable_chars)).decode('utf-8')


class FileHandle(TrifleType):
    def __init__(self, file_name, file_handle, file_mode):
        self.is_closed = False

        assert isinstance(file_name, str), "File name is %r" % file_name
        self.file_name = file_name

        self.file_handle = file_handle
        self.mode = file_mode

    def repr(self):
        return u'#file-handle("%s")' % self.file_name.decode('utf-8')


class Function(TrifleType):
    """A function provided by the interpreter. Subclasses must provide a
    call method. Arguments are passed in after being evaluated.

    """
    def repr(self):
        # todo: we can be more helpful than this
        return u"<built-in function>"


class FunctionWithEnv(TrifleType):
    """A function provided by the interpreter. Subclasses must provide a
    call method that takes arguments and the environment. Arguments
    are passed in after being evaluated.

    """
    def repr(self):
        # todo: we can be more helpful than this
        return u"<built-in function>"


# todo: could we define interpreter Function classes in terms of Lambda?
class Lambda(TrifleType):
    """A user defined function. Holds a reference to the current lexical
    environment, so we support closures.

    """
    def __init__(self, arguments, body, env):
        self.arguments = arguments
        self.body = body
        self.env = env

    def repr(self):
        # todo: we can be more helpful than this
        return u"<lambda>"


class Macro(TrifleType):
    """As with Function, subclasses must provide a call method. Macros are
    evaluated at compile time, and should return an expression for the
    intepreter to evaluate at run time.

    """
    def __init__(self, arguments, body):
        self.arguments = arguments
        self.body = body

    def repr(self):
        # todo: we can be more helpful than this
        return u"<macro>"


class Special(TrifleType):
    """A special expression is an expression whose arguments are passed
    unevaluated, but at run time.

    """
    def repr(self):
        # todo: we can be more helpful than this
        return u"<special expression>"


"""Our parenthesis classes aren't exposed to the user, but we add them
for consistency when boxing values from the lexer.

"""

class OpenParen(TrifleType):
    pass


class CloseParen(TrifleType):
    pass
