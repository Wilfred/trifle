import os
from rpython.rlib.rbigint import rbigint as RBigInt
from rpython.rlib.objectmodel import r_dict

"""Note that 'types' is part of the python standard library, so we're
forced to name this file trifle_types.

RPython ignores magic methods (except __init__) but we implement them
for convenience when testing.

"""

def is_equal(x, y):
    """Return True if x and y are equal.

    TODO: fix the potential stack overflow here for deeply nested
    lists and hashmaps.

    """
    # TODO: Once we have proper interning, we should be able to use `x
    # is y` for symbols and keywords.
    if isinstance(x, Symbol):
        if isinstance(y, Symbol):
            return x.symbol_name == y.symbol_name

        return False

    elif isinstance(x, Keyword):
        if isinstance(y, Keyword):
            return x.symbol_name == y.symbol_name

        return False

    elif isinstance(x, Float):
        if isinstance(y, Float):
            return x.float_value == y.float_value

        elif isinstance(y, Integer):
            # TODO: potentially y could be too big for floats.
            return x.float_value == y.bigint_value.tofloat()

        return False

    elif isinstance(x, Integer):
        if isinstance(y, Integer):
            return x.bigint_value.eq(y.bigint_value)

        elif isinstance(y, Float):
            return x.bigint_value.tofloat() == y.float_value

        return False

    elif isinstance(x, Fraction):
        if isinstance(y, Fraction):
            return (x.numerator == y.numerator and
                    x.denominator == y.denominator)

        elif isinstance(y, Float):
            # TODO: Document the corner cases here when our fractions
            # are bigger than the largest legal float, or can't be represented exactly.
            return is_equal(Float(x.numerator.tofloat() / x.denominator.toint()), y)

        return False

    elif isinstance(x, Character):
        if isinstance(y, Character):
            return x.character == y.character

        return False

    elif isinstance(x, String):
        if isinstance(y, String):
            return x.string == y.string

        return False

    elif isinstance(x, Bytestring):
        if isinstance(y, Bytestring):
            return x.byte_value == y.byte_value

        return False

    elif isinstance(x, List):
        if isinstance(y, List):
            if len(x.values) != len(y.values):
                return False

            for i in range(len(x.values)):
                if not is_equal(x.values[i], y.values[i]):
                    return False
            return True

        return False

    elif isinstance(x, Hashmap):
        if isinstance(y, Hashmap):
            if len(x.dict.keys()) != len(y.dict.keys()):
                return False

            for key, x_value in x.dict.iteritems():
                y_value = y.dict.get(key, None)

                if y_value is None:
                    return False
                elif not is_equal(x_value, y_value):
                    return False

            return True

        return False

    # In principle, we should only have one instance of #true and of
    # #false. This ensures boolean equality still works even if
    # built-in functions instantiate fresh booleans.
    elif isinstance(x, Boolean):
        if isinstance(y, Boolean):
            return x.value == y.value

        return False

    return x is y


class TrifleType(object):
    def __eq__(self, other):
        return is_equal(self, other)
    
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
        return unicode(self.bigint_value.str())

    def __eq__(self, other):
        """We deliberately treat Integer(1) as different to Float(1.0) since
        this magic method is only used in tests and it avoids confusion.

        """
        if self.__class__ != other.__class__:
            return False

        return self.bigint_value.eq(other.bigint_value)

    def __init__(self, value):
        assert isinstance(value, RBigInt)
        self.bigint_value = value

    @staticmethod
    def fromstr(s):
        return Integer(RBigInt.fromdecimalstr(s))

    @staticmethod
    def fromint(num):
        assert isinstance(num, int), "Expected Python int but got: %s" % num
        return Integer(RBigInt.fromint(num))


def greatest_common_divisor(a, b):
    """Find the largest number that divides both a and b.
    We use the Euclidean algorithm for simplicity:
    http://en.wikipedia.org/wiki/Euclidean_algorithm

    """
    while not b.eq(RBigInt.fromint(0)):
        temp = b
        b = a.mod(b)
        a = temp

    return a


class Fraction(TrifleType):
    def repr(self):
        return u"%s/%s" % (unicode(self.numerator.str()),
                           unicode(self.denominator.str()))

    def __init__(self, numerator, denominator):
        assert isinstance(numerator, RBigInt)
        assert isinstance(denominator, RBigInt)

        assert denominator.gt(RBigInt.fromint(0))

        common_factor = greatest_common_divisor(
            numerator.abs(), denominator.abs())
        if common_factor.ne(RBigInt.fromint(1)):
            numerator = numerator.div(common_factor)
            denominator = denominator.div(common_factor)
        
        self.numerator = numerator
        self.denominator = denominator


class Float(TrifleType):
    def repr(self):
        return u"%f" % self.float_value

    def __eq__(self, other):
        """We deliberately treat Integer(1) as different to Float(1.0) since
        this magic method is only used in tests and it avoids confusion.

        """
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

    def __init__(self, symbol_name):
        assert isinstance(symbol_name, unicode)
        self.symbol_name = symbol_name


# TODOC
class Keyword(TrifleType):
    def repr(self):
        return u":%s" % self.symbol_name

    def __repr__(self):
        return "<%s: %s>" % (self.__class__.__name__, self.symbol_name)

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

    def __init__(self, character):
        assert isinstance(character, unicode)
        assert len(character) == 1

        self.character = character


def hash_trifle_type(trifle_value):
    if isinstance(trifle_value, Integer):
        return trifle_value.bigint_value.hash()
    else:
        assert False, "TODO: hash more Trifle types."


class Hashmap(TrifleType):
    def __init__(self):
        self.dict = r_dict(is_equal, hash_trifle_type)

    def __eq__(self, other):
        return is_equal(self, other)

    def __repr__(self):
        return self.repr()

    # TODO: fix infinite loop for hashmaps that contain themselves.
    def repr(self):
        element_reprs = [key.repr() + u" " + value.repr() for key, value in self.dict.iteritems()]
        return u"{%s}" % u", ".join(element_reprs)


class String(TrifleType):
    def repr(self):
        printable_chars = []
        for char in self.string:
            if char == u'\n':
                printable_chars.append(u"\\n")
            elif char == u'"':
                printable_chars.append(u'\\"')
            elif char == u"\\":
                printable_chars.append(u"\\\\")
            else:
                printable_chars.append(char)
            
        return u'"%s"' % u"".join(printable_chars)

    def __repr__(self):
        return '<String: %s>' % self.repr()

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

    # TODO: fix infinite loop for lists that contain themselves
    def repr(self):
        element_reprs = [element.repr() for element in self.values]
        return u"(%s)" % u" ".join(element_reprs)


class Bytestring(TrifleType):
    def __init__(self, byte_value):
        assert isinstance(byte_value, list), "Expected a list, but got: %s" % byte_value
        if byte_value:
            assert isinstance(byte_value[0], int)
        self.byte_value = byte_value

    def repr(self):
        SMALLEST_PRINTABLE_CHAR = ' '
        LARGEST_PRINTABLE_CHAR = '~'

        printable_chars = []

        for char_code in self.byte_value:
            char = chr(char_code)
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

    def close(self):
        self.is_closed = True
        self.file_handle.close()

    def flush(self):
        self.file_handle.flush()

    def write(self, string):
        self.file_handle.write(string)

    def repr(self):
        return u'#file-handle("%s")' % self.file_name.decode('utf-8')


STDOUT_FILE_DESCRIPTOR = 1


class Stdout(FileHandle):
    
    def __init__(self):
        self.file_name = ""
        self.is_closed = False
        self.mode = Keyword(u'write')

    def close(self):
        self.is_closed = True
        os.close(STDOUT_FILE_DESCRIPTOR)

    def flush(self):
        """This is a Python-specific detail, I believe and we don't need to do
        anything for stdout. Note that Python doesn't provide
        os.flush(file_descriptor).
        
        TODO: consider removing `flush!` entirely.

        """
        pass

    def write(self, string):
        os.write(STDOUT_FILE_DESCRIPTOR, string)

    def repr(self):
        return u'#file-handle(stdout)'



class Function(TrifleType):
    """A function provided by the interpreter. Subclasses must provide a
    call method. Arguments are passed in after being evaluated.

    """
    def repr(self):
        # todo: we can be more helpful than this
        return u"<built-in function>"


# TODO: rename this, since it also takes the stack as an argument.
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


# TODO: decide on whether we want to use the term 'error' or
# 'exception', and use it consistently.
class TrifleExceptionType(TrifleType):
    """We catch exceptions by type. An exception type may declare a parent
    (i.e. single inheritance).

    Catching the parent exception will also catch any exception that
    inherits from it.

    """
    def __init__(self, parent, name):
        assert isinstance(name, unicode), \
            "Exception type names must be unicode strings, but got %r" % name
        self.name = name

        if parent is None:
            self.parent = None
        else:
            assert isinstance(parent, TrifleExceptionType)
            self.parent = parent

    def repr(self):
        return u'#error-type("%s")' % self.name


class TrifleExceptionInstance(TrifleType):
    def __init__(self, exception_type, message):
        assert isinstance(exception_type, TrifleExceptionType)
        self.exception_type = exception_type
        
        assert isinstance(message, unicode)
        self.message = message

        self.caught = False

    def repr(self):
        # TODO: show the message too.
        return u'#error(%s)' % self.exception_type.name

    def __repr__(self):
        return '<%s: %s>' % (self.exception_type.name, self.message)


class Macro(TrifleType):
    """As with Function, subclasses must provide a call method. Macros are
    evaluated at compile time, and should return an expression for the
    intepreter to evaluate at run time.

    """
    def __init__(self, name, arguments, body):
        self.name = name
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


class OpenCurlyParen(TrifleType):
    pass


class CloseCurlyParen(TrifleType):
    pass
