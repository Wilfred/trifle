# Sadly, re isn't available in rpython.
from rpython.rlib.rsre import rsre_core
from rpython.rlib.rsre.rpy import get_code

from trifle_types import (OpenParen, CloseParen, Integer, Float,
                          Symbol, Keyword,
                          String, TRUE, FALSE, NULL)
from errors import LexFailed


# Note this an incomplete list.
WHITESPACE = 'whitespace'
COMMENT = 'comment'
OPEN_PAREN = 'open-paren'
CLOSE_PAREN = 'close-paren'
INTEGER = 'integer'
SYMBOL = 'symbol'
KEYWORD = 'keyword'
STRING = 'string'
FLOAT = 'float'

# TODO: support 0x123, 0o123
INTEGER_REGEXP = get_code('-?[0-9_]+')

# todoc: exactly what syntax we accept for numbers and symbols
TOKENS = [
    (WHITESPACE, get_code(r"\s+")),
    (COMMENT, get_code(";[^\n]*")),
    (OPEN_PAREN, get_code(r"\(")),
    (CLOSE_PAREN, get_code(r"\)")),

    # todoc
    # todo: support single quoted strings
    (STRING, get_code(r"\"[^\"\\]*\"")),

    # todoc
    (FLOAT, get_code(r"-?[0-9_]+\.[0-9_]+")),

    # note this captures true/false/null and integers too
    (SYMBOL, get_code('[a-z0-9*/+?!<>=_-][a-z0-9*/+?!<>=_-]*')),
    
    (KEYWORD, get_code(':[a-z*/+?!<>=_-][a-z0-9*/+?!<>=_-]*')),
]

DIGITS = '0123456789'

def starts_like_integer(text):
    if not text:
        return False

    if text[0] in DIGITS:
        return True

    if len(text) > 1:
        if text[0] == '-' and text[1] in DIGITS:
            return True

    return False


def remove_char(string, unwanted_char):
    """Return string with all instances of char removed.  We're forced to
    iterate over a list to keep RPython happy.

    """
    chars = []
    for char in string:
        if char != unwanted_char:
            chars.append(char)

    return "".join(chars)


def lex(text):
    lexed_tokens = []

    while text:
        found_match = False
    
        for token, regexp in TOKENS:
            match = rsre_core.match(regexp, text)
            if match:
                found_match = True

                if token in [WHITESPACE, COMMENT]:
                    pass
                elif token == OPEN_PAREN:
                    lexed_tokens.append(OpenParen())
                elif token == CLOSE_PAREN:
                    lexed_tokens.append(CloseParen())
                elif token == SYMBOL:
                    # We deliberately treat `true`, `false` and `null`
                    # as literals rather than just variables defined.
                    # Otherwise, an expression may print `true` as its
                    # result but evaluating `true` may not give
                    # `true`, which is confusing.
                    if text[:match.match_end] == 'true':
                        lexed_tokens.append(TRUE)
                    elif text[:match.match_end] == 'false':
                        lexed_tokens.append(FALSE)
                    elif text[:match.match_end] == 'null':
                        lexed_tokens.append(NULL)
                    elif starts_like_integer(text[:match.match_end]):
                        integer_string = remove_char(text[:match.match_end], "_")
                        try:
                            lexed_tokens.append(Integer(int(integer_string)))
                        except ValueError:
                            raise LexFailed("Invalid number: '%s'" % text)
                        
                    else:
                        lexed_tokens.append(Symbol(text[:match.match_end]))
                elif token == FLOAT:
                    float_string = remove_char(text[:match.match_end], "_")
                    lexed_tokens.append(Float(float(float_string)))
                elif token == KEYWORD:
                    # todoc
                    lexed_tokens.append(Keyword(text[1:match.match_end]))
                elif token == STRING:
                    # todoc
                    string_end = match.match_end - 1

                    # This is always true, but RPython doesn't support
                    # negative indexes on slices and can't prove the
                    # slice is non-negative.
                    if string_end >= 0:
                        lexed_tokens.append(String(text[1:string_end]))
                else:
                    assert False, "Unrecognised token '%s'" % token
                
                text = text[match.match_end:]
                break

        if not found_match:
            raise LexFailed("Could not lex remainder: '%s'" % text)

    return lexed_tokens
