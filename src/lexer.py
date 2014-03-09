# Sadly, re isn't available in rpython.
from rpython.rlib.rsre import rsre_core
from rpython.rlib.rsre.rpy import get_code

from trifle_types import (OpenParen, CloseParen, Integer, Float,
                          Symbol, Keyword,
                          String, Bytestring, Character,
                          TRUE, FALSE, NULL)
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
CHARACTER = 'character'
BYTESTRING = 'bytestring'
FLOAT = 'float'
BOOLEAN = 'boolean'
NULL_TYPE = 'null type'
ATOM = 'atom'
HASH_LITERAL = 'hash_literal'

# Tokens are used to split strings into coarse categories.
TOKENS = [
    (WHITESPACE, get_code(r"\s+")),
    (COMMENT, get_code(";[^\n]*")),
    (OPEN_PAREN, get_code(r"\(")),
    (CLOSE_PAREN, get_code(r"\)")),

    (ATOM, get_code('[:a-z0-9*/+?!<>=_.-]+')),
    (STRING, get_code(r'"[^"\\]*"')),
    (CHARACTER, get_code(r"'[^'\\]'")),

    (BYTESTRING, get_code(r'#bytes\("[ -~]*"\)')),

    (HASH_LITERAL, get_code('#[a-zA-Z]*')),
]

# After splitting, we lex properly.
LEXEMES = [
    (OPEN_PAREN, get_code(r"\(")),
    (CLOSE_PAREN, get_code(r"\)")),

    # todo: support some backslash patterns
    (STRING, get_code(r"\"[^\"\\]*\"$")),
    (BYTESTRING, get_code(r'#bytes\("[ -~]*"\)')),
    (CHARACTER, get_code(r"'[^']'")),

    (FLOAT, get_code(r"-?[0-9_]+\.[0-9_]+$")),

    # TODO: support 0x123, 0o123
    (INTEGER, get_code('-?[0-9_]+$')),

    (BOOLEAN, get_code('(#true|#false)$')),
    (NULL_TYPE, get_code('#null$')),
    
    # todoc: exactly what syntax we accept for symbols
    (SYMBOL, get_code('[a-z*/+?!<>=_-][a-z0-9*/+?!<>=_-]*$')),
    (KEYWORD, get_code(':[a-z*/+?!<>=_-][a-z0-9*/+?!<>=_-]*$')),
]

DIGITS = u'0123456789'

def starts_like_integer(text):
    if not text:
        return False

    if text[0] in DIGITS:
        return True

    if len(text) > 1:
        if text[0] == u'-' and text[1] in DIGITS:
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
            raise LexFailed(u"Could not lex remainder: '%s'" % text)

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
                    
                elif lexeme_name == BOOLEAN:
                    if token == u'#true':
                        lexed_tokens.append(TRUE)
                    else:
                        lexed_tokens.append(FALSE)
                elif lexeme_name == NULL_TYPE:
                    lexed_tokens.append(NULL)
                    
                elif lexeme_name == INTEGER:
                    integer_string = remove_char(token, "_")
                    try:
                        lexed_tokens.append(Integer(int(integer_string)))
                    except ValueError:
                        raise LexFailed(u"Invalid integer: '%s'" % token)
                        
                elif lexeme_name == FLOAT:
                    float_string = remove_char(token, "_")
                    try:
                        lexed_tokens.append(Float(float(float_string)))
                    except ValueError:
                        raise LexFailed(u"Invalid float: '%s'" % token)

                elif lexeme_name == SYMBOL:
                    lexed_tokens.append(Symbol(token))
                elif lexeme_name == KEYWORD:
                    # todoc
                    lexed_tokens.append(Keyword(token[1:]))
                elif lexeme_name == STRING:
                    string_end = match.match_end - 1

                    # This is always true, but RPython doesn't support
                    # negative indexes on slices and can't prove the
                    # slice is non-negative.
                    if string_end >= 0:
                        string_contents = token[1:string_end]
                        lexed_tokens.append(String([char for char in string_contents]))
                elif lexeme_name == BYTESTRING:
                    string_end = match.match_end - 2

                    # This is always true, but RPython doesn't support
                    # negative indexes on slices and can't prove the
                    # slice is non-negative.
                    if string_end >= 0:
                        contents = token[8:string_end]
                    else:
                        # Unreachable.
                        contents = u""

                    lexed_tokens.append(Bytestring(bytearray(contents.encode("utf-8"))))
                elif lexeme_name == CHARACTER:
                    lexed_tokens.append(Character(token[1]))
                else:
                    assert False, u"Unrecognised token '%s'" % token
                
                break

        if not found_match:
            raise LexFailed(u"Could not lex token: '%s'" % token)

    return lexed_tokens


def lex(text):
    return _lex(split_tokens(text))
