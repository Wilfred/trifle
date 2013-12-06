
# TODO: eventually we want users to be able to catch any of these
# errors at runtime

class TrifleError(Exception):
    pass

class UnboundVariable(TrifleError):
    pass


# Python already has a 'TypeError' exception
class TrifleTypeError(TrifleError):
    pass
