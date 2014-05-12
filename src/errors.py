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
    

class UnboundVariable(TrifleError):
    pass


# Base exception.
error = TrifleExceptionType(None, u"error")


no_such_variable = TrifleExceptionType(error, u"no-such-variable")


wrong_type = TrifleExceptionType(error, u"wrong-type")


wrong_argument_number = TrifleExceptionType(error, u"wrong-argument-number")


# Python already has a 'TypeError' exception
class TrifleTypeError(TrifleError):
    pass

    
class ArityError(TrifleError):
    pass


class DivideByZero(TrifleError):
    pass


division_by_zero = TrifleExceptionType(error, u"division-by-zero")


class StackOverflow(TrifleError):
    pass


class FileNotFound(TrifleError):
    pass


class TrifleValueError(TrifleError):
    pass


class UsingClosedFile(TrifleError):
    pass
