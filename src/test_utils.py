from cStringIO import StringIO
from contextlib import contextmanager

from mock import patch

from evaluator import evaluate
from main import env_with_prelude


def evaluate_with_prelude(expression):
    return evaluate(expression, env_with_prelude())


@contextmanager
def mock_stdout():
    """Temporarily patch sys.stdout and return the StringIO buffer that
    was written to.

    """
    fake_stdout = StringIO()

    with patch('sys.stdout', fake_stdout):
        yield fake_stdout


# TODO: fix duplication with contextmanager above.
@contextmanager
def mock_stdout_fd():
    with patch('os.write') as patched:
        yield patched
