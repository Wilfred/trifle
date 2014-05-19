import os

from trifle_types import List

"""Functions which are built-in to Python, but aren't defined or can't
be typed in RPython. So, we define our own here.

"""


def raw_input(prefix):
    """Assumes the input is no more than 1024 characters, and always
    returns a unicode object.

    Based on http://stackoverflow.com/a/9244639

    """
    STDIN = 0
    STDOUT = 1
    os.write(STDOUT, prefix.encode('utf-8'))

    user_string = os.read(STDIN, 1024)[:-1] # discard the trailing last newline
    return user_string.decode('utf-8')


def zip(list1, list2):
    """Unlike Python's zip(), only allows two arguments, and assumes lists."""
    length = min(len(list1), len(list2))

    result = []
    for i in range(length):
        result.append((list1[i], list2[i]))

    return result


# todo: fix potential stack overflow
def deepcopy(value):
    """Assumes that the value is a Trifle type.

    """
    if isinstance(value, List):
        return List([
            deepcopy(item) for item in value.values
        ])
    else:
        return value


def copy(value):
    """Assumes that the value is a Trifle type.

    """
    if isinstance(value, List):
        return List([item for item in value.values])
    else:
        return value


# Not sure why RPython doesn't permit list(dynamic_unicode_value).
def list(value):
    return [x for x in value]
