from trifle_types import Function, Integer
from errors import TrifleTypeError


class Addition(Function):
    def call(self, args):
        for arg in args:
            # todo: we will want other numeric types
            if not isinstance(arg, Integer):
                # todoc: this error
                raise TrifleTypeError(
                    "%s is not a number." % arg.repr())

        total = 0
        for arg in args:
            total += arg.value
        return Integer(total)


class Subtraction(Function):
    def call(self, args):
        for arg in args:
            # todo: we will want other numeric types
            if not isinstance(arg, Integer):
                # todoc: this error
                raise TrifleTypeError(
                    "%s is not a number." % arg.repr())

        if not args:
            return Integer(0)

        if len(args) == 1:
            return Integer(-args[0].value)

        total = args[0].value
        for arg in args[1:]:
            total -= arg.value
        return Integer(total)

