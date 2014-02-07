
# TODO: eventually we want users to be able to catch any of these
# errors at runtime

class TrifleError(Exception):
    # .message isn't available in RPython, so we manually assign it.
    # todo: file a pypy to improve their docs
    def __init__(self, message):
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


# Python already has a 'TypeError' exception
# TODO: add a value error too
class TrifleTypeError(TrifleError):
    pass

    
class ArityError(TrifleError):
    pass


class DivideByZero(TrifleError):
    pass


class StackOverflow(TrifleError):
    pass


class FileNotFound(TrifleError):
    pass


class TrifleValueError(TrifleError):
    pass
