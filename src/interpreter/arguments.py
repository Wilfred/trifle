from trifle_types import List
from errors import ArityError


# Normally we'd use None for this, but RPython doesn't like mixing
# None and integers.
ANY = -1


# TODO: ideally we'd name the arguments we're expected
def check_args(name, args, min=ANY, max=ANY):
    """Check whether args is the right length for this function or special
    expression.

    args is a Python list.

    """
    if min == max:
        if len(args) != min:
            if min == 1:
                raise ArityError(
                    u"%s takes 1 argument, but got %d: %s" % (name, len(args), List(args).repr())
                )
            else:
                raise ArityError(
                    u"%s takes %d arguments, but got %d: %s" % (name, min, len(args), List(args).repr())
                )

    elif max == ANY:
        if len(args) < min:
            if min == 1:
                raise ArityError(
                    u"%s takes at least 1 argument, but got %d: %s" % (name, len(args), List(args).repr())
                )
            else:
                raise ArityError(
                    u"%s takes at least %d arguments, but got %d: %s" % (name, min, len(args), List(args).repr())
                )

    else:
        if not (min <= len(args) <= max):
            raise ArityError(
                u"%s takes between %d and %d arguments, but got %d: %s" % (name, min, max, len(args), List(args).repr())
            )
