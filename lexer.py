# Sadly, re isn't available in rpython.
from rpython.rlib.rsre import rsre_core
from rpython.rlib.rsre.rpy import get_code

from trifle_types import OpenParen, CloseParen, Integer, Symbol
from errors import LexFailed


WHITESPACE = 'whitespace'
COMMENT = 'comment'
OPEN_PAREN = 'open-paren'
CLOSE_PAREN = 'close-paren'
INTEGER = 'integer'
SYMBOL = 'symbol'

TOKENS = [
    (WHITESPACE, get_code(r"\s+")),
    (COMMENT, get_code(";[^\n]*")),
    (OPEN_PAREN, get_code(r"\(")),
    (CLOSE_PAREN, get_code(r"\)")),

    # todo: it'd be nice to allow number literals with underscores,
    # e.g. 1_000_000
    (INTEGER, get_code('-?[0-9]+')),

    (SYMBOL, get_code('[a-z*/+?-][a-z0-9*/+?-]*')),
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
                    lexed_tokens.append(Integer(int(text[:match.match_end])))
                elif token == SYMBOL:
                    lexed_tokens.append(Symbol(text[:match.match_end]))
                else:
                    assert False, "Unrecognised token '%s'" % token
                
                text = text[match.match_end:]
                break

        if not found_match:
            raise LexFailed("Could not lex remainder: '%s'" % text)

    return lexed_tokens
