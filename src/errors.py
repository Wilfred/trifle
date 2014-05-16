from trifle_types import TrifleExceptionType


class TrifleError(Exception):
    # .message isn't available in RPython, so we manually assign it.
    # todo: file a pypy bug to improve their docs
    def __init__(self, message):
        assert isinstance(message, unicode)
        self.message = message

    def __str__(self):
        # Ignored by RPython, but useful for debugging
        return self.message


class LexFailed(TrifleError):
    pass


class ParseFailed(TrifleError):
    pass
    

# Base exception.
error = TrifleExceptionType(None, u"error")


no_such_variable = TrifleExceptionType(error, u"no-such-variable")


# TODO: we need a syntax-error too, since (try x #null) and (let (1 1))
# can be checked at compile time and don't depend on runtime types.
wrong_type = TrifleExceptionType(error, u"wrong-type")


wrong_argument_number = TrifleExceptionType(error, u"wrong-argument-number")


class ArityError(TrifleError):
    pass


division_by_zero = TrifleExceptionType(error, u"division-by-zero")


class StackOverflow(TrifleError):
    pass


class FileNotFound(TrifleError):
    pass


class TrifleValueError(TrifleError):
    pass


# TODO: find a better name here
changing_closed_handle = TrifleExceptionType(error, u"changing-closed-handle")
