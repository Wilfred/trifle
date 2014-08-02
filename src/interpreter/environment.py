from built_ins import (
    Add, Subtract, Multiply, Divide, Mod, Div,
    LessThan, Same, Equal,
    Quote, SetSymbol, Let, If, While,
    LambdaFactory, DefineMacro, ExpandMacro, FreshSymbol,
    Length, SymbolPredicate, ListPredicate, StringPredicate,
    BytestringPredicate, CharacterPredicate,
    GetIndex, SetIndex, Insert,
    Printable, Input, Exit,
    Call, Parse, Eval, Defined, Try,
    Open, Close, Read, Write, Flush,
    Encode, Decode,
    Throw, Message, ExceptionType,
)
from errors import (
    error, stack_overflow, no_such_variable, parse_failed,
    lex_failed, value_error, wrong_type,
    wrong_argument_number, division_by_zero,
    file_not_found, changing_closed_handle,
)
from trifle_types import (
    String, Stdout)
from almost_python import list


class Scope(object):
    def __init__(self, bindings):
        self.bindings = bindings

    def __repr__(self):
        return "<%s: %r>" % (self.__class__.__name__, sorted(self.bindings.keys()))

    def contains(self, symbol):
        return symbol in self.bindings

    def get(self, symbol):
        # Note this raises KeyError if the variable name is not
        # present, unlike .get on dict objects.
        return self.bindings[symbol]

    def set(self, symbol, value):
        self.bindings[symbol] = value


# TODO: This is also used inside try-catch, so we should find a better
# name for it.
class LetScope(Scope):
    """Behaves as a normal function scope, but only allows variables to be
    defined inside the first argument to `let`.

    """
    pass

class Environment(object):
    """All variable bindings are stored in an environment. It handles
    nested scope by using a list of dicts, where the first dict is for
    globals and so on.

    """
    def __init__(self, scopes):
        self.scopes = scopes

    def __repr__(self):
        return "<Environment %r>" % self.scopes

    # we can't use __get__ and __set__ in RPython, so we use normal methods
    def get(self, variable_name):
        # Note this raises KeyError if the variable name is not
        # present, unlike .get on dict objects.

        # We search scopes starting at the innermost.
        for scope in reversed(self.scopes):
            if scope.contains(variable_name):
                return scope.get(variable_name)

        raise KeyError(u"Could not find '%s' in environment" % variable_name)

    def globals_only(self):
        """Return a new environment that only includes variables defined
        globally.

        """
        return Environment([self.scopes[0]])

    def set(self, symbol, value):
        assert isinstance(symbol, unicode)
        
        # If the variable is already defined, update it in the
        # innermost scope that it is defined in.
        for scope in reversed(self.scopes):
            if scope.contains(symbol):
                scope.set(symbol, value)
                return

        # Otherwise, define and set it in the very innermost scope that isn't a let scope.
        for scope in reversed(self.scopes):
            if not isinstance(scope, LetScope):
                scope.set(symbol, value)

    def set_global(self, variable_name, value):
        self.scopes[0].set(variable_name, value)

    def contains(self, variable_name):
        for scope in reversed(self.scopes):
            if scope.contains(variable_name):
                return True

        return False

    def with_nested_scope(self, inner_scope):
        """Return a new environment that shares all the outer scopes with this
        environment, but has an additional inner scope.

        """
        return Environment(self.scopes + [inner_scope])


# TODO: expose this as a runtime variable
special_expressions = {
    u'let': Let(),
    u'if': If(),
    u'while': While(),
    u'lambda': LambdaFactory(),
    u'macro': DefineMacro(),
    u'expand-macro': ExpandMacro(),
    u'quote': Quote(),
    u'try': Try(),
}


def fresh_environment():
    """Return a new environment that only contains the built-ins.

    """
    return Environment([Scope({
        # Functions.
        u'+': Add(),
        u'-': Subtract(),
        u'*': Multiply(),
        u'/': Divide(),
        u'mod': Mod(),
        u'div': Div(),
        u'<': LessThan(),
        u'length': Length(),
        u'symbol?': SymbolPredicate(),
        u'list?': ListPredicate(),
        u'string?': StringPredicate(),
        u'bytestring?': BytestringPredicate(),
        u'character?': CharacterPredicate(),
        u'get-index': GetIndex(),
        u'set-index!': SetIndex(),
        u'insert!': Insert(),
        u'same?': Same(),
        u'equal?': Equal(),
        u'set-symbol!': SetSymbol(),
        u'fresh-symbol': FreshSymbol(),
        u'printable': Printable(),
        u'input': Input(),
        u'exit!': Exit(),
        u'call': Call(),
        u'parse': Parse(),
        u'eval': Eval(),
        u'defined?': Defined(),
        u'open': Open(),
        u'close!': Close(),
        u'read': Read(),
        u'write!': Write(),
        u'flush!': Flush(),
        u'encode': Encode(),
        u'decode': Decode(),
        u'throw': Throw(),
        u'message': Message(),
        u'exception-type': ExceptionType(),

        # Exception types.
        u'error': error,
        u'stack-overflow': stack_overflow,
        u'no-such-variable': no_such_variable,
        u'parse-failed': parse_failed,
        u'lex-failed': lex_failed,
        u'value-error': value_error,
        u'wrong-type': wrong_type,
        u'wrong-argument-number': wrong_argument_number,
        u'division-by-zero': division_by_zero,
        u'file-not-found': file_not_found,
        u'changing-closed-handle': changing_closed_handle,

        # Constants
        u'VERSION': String(list(u"0.9")),

        # Standard I/O.
        u'stdout': Stdout(),
    })])
