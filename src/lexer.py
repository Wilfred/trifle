# Sadly, re isn't available in rpython.
from rpython.rlib.rsre import rsre_core
from rpython.rlib.rsre.rpy import get_code

from trifle_types import (OpenParen, CloseParen, Integer, Float,
                          Symbol, Keyword,
                          String, TRUE, FALSE, NULL)
from errors import LexFailed


# Note this an incomplete list and is purely to give us convenient
# constants.
WHITESPACE = 'whitespace'
COMMENT = 'comment'
OPEN_PAREN = 'open-paren'
CLOSE_PAREN = 'close-paren'
INTEGER = 'integer'
SYMBOL = 'symbol'
KEYWORD = 'keyword'
STRING = 'string'
FLOAT = 'float'
ATOM = 'atom'

ATOM_REGEXP = get_code('[a-z0-9*/+?!<>=_-][a-z0-9*/+?!<>=_-]*')

# TODO: support 0x123, 0o123
INTEGER_REGEXP = get_code('-?[0-9_]+')

# todoc: exactly what syntax we accept for symbols
TOKENS = [
    (WHITESPACE, get_code(r"\s+")),
    (COMMENT, get_code(";[^\n]*")),
    (OPEN_PAREN, get_code(r"\(")),
    (CLOSE_PAREN, get_code(r"\)")),

    (ATOM, get_code('[:a-z0-9*/+?!<>=_.-]+')),
    (STRING, get_code(r"\"[^\"\\]*\"")),
]

LEXEMES = [
    (OPEN_PAREN, get_code(r"\(")),
    (CLOSE_PAREN, get_code(r"\)")),

    # todoc
    # todo: support single quoted characters
    (STRING, get_code(r"\"[^\"\\]*\"")),

    # todoc
    (FLOAT, get_code(r"-?[0-9_]+\.[0-9_]+")),

    # note this captures true/false/null and integers too
    # TODO: fix that
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


def split_tokens(text):
    """Given the raw text of a trifle program, split it into things that
    look like tokens.

    """
    tokens = []

    while text:
        found_match = False
    
        for token, regexp in TOKENS:
            match = rsre_core.match(regexp, text)
            if match:
                found_match = True
                matched_text = text[:match.match_end]
                text = text[match.match_end:]

                if token in [WHITESPACE, COMMENT]:
                    pass
                else:
                    tokens.append(matched_text)
                
                break

        if not found_match:
            raise LexFailed("Could not lex remainder: '%s'" % text)

    return tokens


def _lex(tokens):
    lexed_tokens = []

    for token in tokens:
        found_match = False
    
        for lexeme_name, regexp in LEXEMES:
            match = rsre_core.match(regexp, token)
            if match:
                found_match = True

                if lexeme_name in [WHITESPACE, COMMENT]:
                    pass
                elif lexeme_name == OPEN_PAREN:
                    lexed_tokens.append(OpenParen())
                elif lexeme_name == CLOSE_PAREN:
                    lexed_tokens.append(CloseParen())
                elif lexeme_name == SYMBOL:
                    # We deliberately treat `true`, `false` and `null`
                    # as literals rather than just variables defined.
                    # Otherwise, an expression may print `true` as its
                    # result but evaluating `true` may not give
                    # `true`, which is confusing.
                    if token == 'true':
                        lexed_tokens.append(TRUE)
                    elif token == 'false':
                        lexed_tokens.append(FALSE)
                    elif token == 'null':
                        lexed_tokens.append(NULL)
                    elif starts_like_integer(token):
                        integer_string = remove_char(token, "_")
                        try:
                            lexed_tokens.append(Integer(int(integer_string)))
                        except ValueError:
                            raise LexFailed("Invalid integer: '%s'" % token)
                        
                    else:
                        lexed_tokens.append(Symbol(token))
                elif lexeme_name == FLOAT:
                    float_string = remove_char(token, "_")
                    try:
                        lexed_tokens.append(Float(float(float_string)))
                    except ValueError:
                        raise LexFailed("Invalid float: '%s'" % token)
                elif lexeme_name == KEYWORD:
                    # todoc
                    lexed_tokens.append(Keyword(token[1:]))
                elif lexeme_name == STRING:
                    # todoc
                    string_end = match.match_end - 1

                    # This is always true, but RPython doesn't support
                    # negative indexes on slices and can't prove the
                    # slice is non-negative.
                    if string_end >= 0:
                        lexed_tokens.append(String(token[1:string_end]))
                else:
                    assert False, "Unrecognised token '%s'" % token
                
                break

        if not found_match:
            raise LexFailed("Could not lex token: '%s'" % token)

    return lexed_tokens


def lex(text):
    return _lex(split_tokens(text))
