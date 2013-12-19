
# TODO: eventually we want users to be able to catch any of these
# errors at runtime

class TrifleError(Exception):
    # .message isn't available in RPython, so we manually assign it.
    # todo: file a pypy to improve their docs
    def __init__(self, message):
        self.message = message


class LexFailed(TrifleError):
    pass


class ParseFailed(TrifleError):
    pass
    

class UnboundVariable(TrifleError):
    pass


# Python already has a 'TypeError' exception
class TrifleTypeError(TrifleError):
    pass
