# There's already a 'parser' in the Python standard library, so we're
# forced to call this trifle_parser.py.

from trifle_types import (
    List, Hashmap,
    OpenParen, CloseParen, OpenCurlyParen, CloseCurlyParen,
    TrifleExceptionInstance)
from errors import parse_failed
from interpreter.hashable import check_hashable


def list_to_hashmap(trifle_list):
    """Convert (1 2 3 4) to {1 2, 3 4}, checking all the corner cases.

    """
    if len(trifle_list.values) % 2 != 0:
        # TODO: This should be a syntax error.
        return TrifleExceptionInstance(
            parse_failed,
            u'Hashmaps must have an even number of elements, but got %d!' % len(trifle_list.values))

    # TODO: Once we have immutable containers, we should allow these as keys too.
    keys = []
    values = []
    for i in range(len(trifle_list.values) / 2):
        keys.append(trifle_list.values[2 * i])
        values.append(trifle_list.values[2 * i + 1])

    is_hashable_error = check_hashable(keys)
    if isinstance(is_hashable_error, TrifleExceptionInstance):
        return is_hashable_error

    hashmap = Hashmap()
    for i in range(len(keys)):
        hashmap.dict[keys[i]] = values[i]

    return hashmap


def parse_inner(tokens, top_level, expecting_list):
    parsed_expressions = List()
    saw_closing_paren = False

    # TODO: This could cause a stack overflow for deeply nested literals.
    while tokens:
        token = tokens.pop(0)

        if isinstance(token, OpenParen):
            parsed = parse_inner(tokens, top_level=False, expecting_list=True)

            if isinstance(parsed, TrifleExceptionInstance):
                return parsed

            parsed_expressions.append(parsed)
        elif isinstance(token, OpenCurlyParen):
            parsed = parse_inner(tokens, top_level=False, expecting_list=False)

            if isinstance(parsed, TrifleExceptionInstance):
                return parsed
                
            parsed_expressions.append(parsed)
        elif isinstance(token, CloseParen):
            if top_level:
                return TrifleExceptionInstance(
                    parse_failed,
                    u'Closing ) has no matching opening (.')
            elif not expecting_list:
                return TrifleExceptionInstance(
                    parse_failed,
                    u'Closing ) does not match opening {.')
            else:
                saw_closing_paren = True
                break
        elif isinstance(token, CloseCurlyParen):
            if top_level:
                return TrifleExceptionInstance(
                    parse_failed,
                    u'Closing } has no matching opening {.')
            elif expecting_list:
                return TrifleExceptionInstance(
                    parse_failed,
                    u'Closing } does not match opening (.')
            else:
                saw_closing_paren = True
                break
        else:
            parsed_expressions.append(token)

    if not top_level and not saw_closing_paren:
        return TrifleExceptionInstance(
            parse_failed, u'Open paren was not closed.')

    if expecting_list:
        return parsed_expressions
    else:
        return list_to_hashmap(parsed_expressions)


def parse(tokens):
    return parse_inner(tokens.values, top_level=True, expecting_list=True)


def parse_one(tokens):
    """Only return the first expression parsed. Useful when parsing short
    code snippets.

    """
    parse_result = parse(tokens)

    if isinstance(parse_result, TrifleExceptionInstance):
        return parse_result
    else:
        return parse_result.values[0]
