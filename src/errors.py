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


no_such_variable = TrifleExceptionType(u"no-such-variable")


# Python already has a 'TypeError' exception
class TrifleTypeError(TrifleError):
    pass

    
class ArityError(TrifleError):
    pass


class DivideByZero(TrifleError):
    pass


division_by_zero = TrifleExceptionType(u"division-by-zero")


class StackOverflow(TrifleError):
    pass


class FileNotFound(TrifleError):
    pass


class TrifleValueError(TrifleError):
    pass


class UsingClosedFile(TrifleError):
    pass
