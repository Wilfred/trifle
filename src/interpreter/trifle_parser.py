# There's already a 'parser' in the Python standard library, so we're
# forced to call this trifle_parser.py.

from trifle_types import List, OpenParen, CloseParen, TrifleExceptionInstance
from errors import parse_failed


def parse_inner(tokens, top_level):
    parse_tree = List()
    saw_closing_paren = False

    while tokens:
        token = tokens.pop(0)

        if isinstance(token, OpenParen):
            parsed = parse_inner(tokens, top_level=False)

            if isinstance(parsed, TrifleExceptionInstance):
                return parsed
                
            parse_tree.append(parsed)
        elif isinstance(token, CloseParen):
            if top_level:
                return TrifleExceptionInstance(
                    parse_failed,
                    u'Closing paren does not have matching open paren.')
            else:
                saw_closing_paren = True
                break
        else:
            parse_tree.append(token)

    if not top_level and not saw_closing_paren:
        return TrifleExceptionInstance(
            parse_failed, u'Open paren was not closed.')

    return parse_tree


def parse(tokens):
    return parse_inner(tokens.values, True)


def parse_one(tokens):
    """Only return the first expression parsed. Useful when parsing short
    code snippets.

    """
    parse_result = parse(tokens)

    if isinstance(parse_result, TrifleExceptionInstance):
        return parse_result
    else:
        return parse_result.values[0]
