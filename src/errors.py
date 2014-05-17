from trifle_types import TrifleExceptionType


"""Internal errors. These are only used inside the interpreter and
never exposed to the user.

"""


class TrifleError(Exception):
    # .message isn't available in RPython, so we manually assign it.
    # todo: file a pypy bug to improve their docs
    def __init__(self, message):
        assert isinstance(message, unicode)
        self.message = message

    def __str__(self):
        # Ignored by RPython, but useful for debugging
        return self.message


class ArityError(TrifleError):
    pass


class LexFailed(TrifleError):
    pass



"""External errors. These may be thrown and caught by users.

TODO: add CPython assertion to ensure that all TrifleExceptionType instances
are defined in the global environment.

"""


# Base exception.
error = TrifleExceptionType(None, u"error")


stack_overflow = TrifleExceptionType(error, u"stack-overflow")


no_such_variable = TrifleExceptionType(error, u"no-such-variable")


# TODO: parse and lex errors should distinuish between bad input and
# incomplete input, so our REPL knows when input is incomplete.
parse_failed = TrifleExceptionType(error, u"parse-failed")


# TODO: this name is a Pythonism, can we do better?
value_error = TrifleExceptionType(error, u"value-error")


# TODO: we need a syntax-error too, since (try x #null) and (let (1 1))
# can be checked at compile time and don't depend on runtime types.
wrong_type = TrifleExceptionType(error, u"wrong-type")


wrong_argument_number = TrifleExceptionType(error, u"wrong-argument-number")


division_by_zero = TrifleExceptionType(error, u"division-by-zero")


# TODO: We should group file errors into a common base exception.
file_not_found = TrifleExceptionType(error, u"file-not-found")


# TODO: find a better name here
changing_closed_handle = TrifleExceptionType(error, u"changing-closed-handle")
