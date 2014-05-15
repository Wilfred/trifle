# Sadly, re isn't available in rpython.
from rpython.rlib.rsre import rsre_core
from rpython.rlib.rsre.rpy import get_code

from trifle_types import (
    OpenParen, CloseParen,
    Integer, Float, Fraction,
    TrifleExceptionInstance,
    Symbol, Keyword, List,
    String, Bytestring, Character,
    TRUE, FALSE, NULL)
from errors import LexFailed, division_by_zero


# Note this an incomplete list and is purely to give us convenient
# constants.
WHITESPACE = 'whitespace'
COMMENT = 'comment'
OPEN_PAREN = 'open-paren'
CLOSE_PAREN = 'close-paren'
INTEGER = 'integer'
FRACTION = 'fraction'
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
    (STRING, get_code(r'"([^"\\]|\\\\|\\n|\\")*\"')),
    (CHARACTER, get_code(r"'([^'\\]|\\\\|\\n|\\')'")),

    (BYTESTRING, get_code(r'#bytes\("[a-zA-Z0-9\\]*"\)')),

    (HASH_LITERAL, get_code('#[a-zA-Z]*')),
]

# After splitting, we lex properly.
LEXEMES = [
    (OPEN_PAREN, get_code(r"\(")),
    (CLOSE_PAREN, get_code(r"\)")),

    (STRING, get_code(r'"([^"\\]|\\\\|\\n|\\")*\"$')),
    (BYTESTRING, get_code(r'#bytes\("[a-zA-Z0-9\\]*"\)')),

    # Either: '\\', '\n', '\'' or a simple character between quotes: 'x'
    (CHARACTER, get_code(r"'([^'\\]|\\\\|\\n|\\')'")),

    (FLOAT, get_code(r"-?[0-9_]+\.[0-9_]+$")),

    # TODO: support 0x123, 0o123
    (INTEGER, get_code('-?[0-9_]+$')),

    (FRACTION, get_code('-?[0-9_]+/[0-9_]+$')),

    (BOOLEAN, get_code('(#true|#false)$')),
    (NULL_TYPE, get_code('#null$')),
    
    # todoc: exactly what syntax we accept for symbols
    (SYMBOL, get_code('[a-z*/+?!<>=_-][a-z0-9*/+?!<>=_-]*$')),
    (KEYWORD, get_code(':[a-z*/+?!<>=_-][a-z0-9*/+?!<>=_-]*$')),
]

DIGITS = u'0123456789'


def remove_char(string, unwanted_char):
    """Return string with all instances of char removed.  We're forced to
    iterate over a list to keep RPython happy.

    """
    chars = []
    for char in string:
        if char != unwanted_char:
            chars.append(char)

    return "".join(chars)

def unescape_chars(string, quote_character):
    """Convert a string with Trifle escape sequences in it to a Python
    string.

    >>> unescape_chars(u'\\"')
    u'"'

    """
    chars = []

    while string:
        if string.startswith(u'\\n'):
            chars.append(u'\n')
            string = string[2:]
        elif string.startswith(u'\\\\'):
            chars.append(u'\\')
            string = string[2:]
        elif string.startswith(u'\\%s' % quote_character):
            chars.append(quote_character)
            string = string[2:]
        else:
            chars.append(string[0])
            string = string[1:]
        
    return chars


def unescape_bytestring_chars(string):
    """Convert a string with Trifle bytestring escape sequences to a Python
    list.

    >>> unescape_chars(u'ab\\x00')
    [97, 98, 0]

    """
    chars = []

    while string:
        if string.startswith(u"\\\\"):
            chars.append(ord('\\'))
            string = string[2:]
        
        # Convert hexadecimal escapes. E.g. \xFF -> 255
        # TODOC
        elif string.startswith(u'\\'):
            if len(string) < 4:
                # TODO: we should give examples of valid escape sequences.
                # (same for strings too)
                raise LexFailed(u"Invalid hexadecimal escape sequence: %s" % string)

            hexadecimal = string[1:4]

            valid_chars = [
                u'a', u'b', u'c', u'd', u'e', u'f',
                u'A', u'B', u'C', u'D', u'E', u'F',
                u'0', u'1', u'2', u'3', u'4', u'5', u'6', u'7', u'8', u'9'
            ]

            if (hexadecimal[0] != u'x' or hexadecimal[1] not in valid_chars
                or hexadecimal[2] not in valid_chars):
                raise LexFailed(u"Invalid hexadecimal escape sequence: %s" % hexadecimal)

            chars.append(int(hexadecimal[1:].encode('utf-8'), 16))
            string = string[4:]
                
        else:
            char = string[0].encode('utf-8')
            # The [0] here is redundant, but RPython needs it to be
            # certain that we only pass a single character to
            # ord(). It can't see that one_char.encode('utf-8) has a length of 1.
            chars.append(ord(char[0]))
            string = string[1:]
        
    return chars


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
            # TODO: It would be nice to suggest where open
            # brackets/quotation marks started, to give the user a hint.
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

                if lexeme_name == OPEN_PAREN:
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

                elif lexeme_name == FRACTION:
                    fraction_string = remove_char(token, "_")
                    fraction_parts = fraction_string.split('/')
                    numerator = fraction_parts[0]
                    denominator = fraction_parts[1]

                    try:
                        numerator = int(numerator)
                        denominator = int(denominator)
                    except ValueError:
                        raise LexFailed(u"Invalid fraction: '%s'" % token)

                    if denominator == 0:
                        return TrifleExceptionInstance(
                            division_by_zero,
                            u"Can't have fraction denominator of zero: '%s'" % token)

                    fraction = Fraction(numerator, denominator)

                    if fraction.denominator == 1:
                        lexed_tokens.append(Integer(fraction.numerator))
                    else:
                        lexed_tokens.append(fraction)

                elif lexeme_name == SYMBOL:
                    lexed_tokens.append(Symbol(token))
                elif lexeme_name == KEYWORD:
                    # todoc
                    lexed_tokens.append(Keyword(token[1:]))
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

                    lexed_tokens.append(Bytestring(unescape_bytestring_chars(contents)))
                    
                elif lexeme_name == STRING:
                    string_end = match.match_end - 1

                    # This is always true, but RPython doesn't support
                    # negative indexes on slices and can't prove the
                    # slice is non-negative.
                    if string_end >= 0:
                        
                        string_contents = token[1:string_end]

                        lexed_tokens.append(String(unescape_chars(string_contents, u'"')))
                elif lexeme_name == CHARACTER:

                    # TODO: use unescape_chars
                    if token == u"'\\n'":
                        lexed_tokens.append(Character(u'\n'))
                    elif token == u"'\\\\'":
                        lexed_tokens.append(Character(u'\\'))
                    elif token == u"'\\''":
                        lexed_tokens.append(Character(u"'"))
                    else:
                        lexed_tokens.append(Character(token[1]))
                else:
                    assert False, u"Unrecognised token '%s'" % token
                
                break

        if not found_match:
            raise LexFailed(u"Could not lex token: '%s'" % token)

    return List(lexed_tokens)


def lex(text):
    return _lex(split_tokens(text))
