from evaluator import evaluate, evaluate_all
from environment import fresh_environment
from main import env_with_prelude


def evaluate_with_prelude(expression):
    return evaluate(expression, env_with_prelude())


def evaluate_all_with_fresh_env(expressions):
    """Evaluate a trifle List of expressions, starting with a fresh environment
    containing only the built-in functions, special expressions and macros.

    """
    return evaluate_all(expressions, fresh_environment())


def evaluate_with_fresh_env(expression):
    return evaluate(expression, fresh_environment())


