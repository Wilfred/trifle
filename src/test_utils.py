from evaluator import evaluate
from main import env_with_prelude


def evaluate_with_prelude(expression):
    return evaluate(expression, env_with_prelude())
