from interpreter.trifle_types import Integer, TrifleExceptionInstance
from interpreter.errors import wrong_type

def check_hashable(values):
    """Check that all the values can be a key in a hashmap. Returns None,
    or a wrong-type exception.

    """
    for value in values:
        if not isinstance(value, Integer):
            # TODO: we may want a more specific error here too.
            # TODO: add support for more types (at least symbols, chars and other types of number)
            return TrifleExceptionInstance(
                wrong_type,
                u"You can't use %s as a hashmap key. Keys must be integers" % value.repr()
            )

    return None
