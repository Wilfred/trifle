# Sadly, re isn't available in rpython.
from rpython.rlib.rsre import rsre_core
from rpython.rlib.rsre.rpy import get_code

from trifle_types import (OpenParen, CloseParen, Integer, Symbol, Keyword,
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

# todoc: exactly what syntax we accept for numbers and symbols
TOKENS = [
    (WHITESPACE, get_code(r"\s+")),
    (COMMENT, get_code(";[^\n]*")),
    (OPEN_PAREN, get_code(r"\(")),
    (CLOSE_PAREN, get_code(r"\)")),

    # todoc
    # todo: support single quoted strings
    (STRING, get_code(r"\"[^\"\\]*\"")),

    # todoc: underscores
    # todo: support 0x123, 0o123
    (INTEGER, get_code('-?[0-9_]+')),

    # note this captures 'true' and 'false' too
    (SYMBOL, get_code('[a-z*/+?!<>=_-][a-z0-9*/+?!<>=_-]*')),
    
    (KEYWORD, get_code(':[a-z*/+?!<>=_-][a-z0-9*/+?!<>=_-]*')),
]


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
                elif token == INTEGER:
                    integer_chars = []
                    for char in text[:match.match_end]:
                        if char != '_':
                            integer_chars.append(char)

                    integer_string = "".join(integer_chars)
                    lexed_tokens.append(Integer(int(integer_string)))
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
                    else:
                        lexed_tokens.append(Symbol(text[:match.match_end]))
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
