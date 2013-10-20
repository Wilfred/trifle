import sys
# Sadly, re isn't available in rpython.
from rpython.rlib.rsre import rsre_core
from rpython.rlib.rsre.rpy import get_code


WHITESPACE = 'whitespace'
OPEN_PAREN = 'open-paren'
CLOSE_PAREN = 'close-paren'
INTEGER = 'integer'


TOKENS = {
    WHITESPACE: get_code(r"\s+")
}


def lex(text):
    lexed_tokens = []

    while True:
        found_match = False
    
        for token, regexp in TOKENS.iteritems():
            match = rsre_core.match(regexp, text)
            if match:
                found_match = True
                lexed_tokens.append((token, text[:match.match_end]))
                text = text[match.match_end:]
                continue

        if not found_match:
            print "Could not lex remainder: '%s'" % text
            break

    return lexed_tokens


def entry_point(argv):
    if len(argv) != 2:
        print "Usage: lexer <code snippet>"
        return 1

    print 'tokens: %s' % lex(argv[1])
    return 0


def target(*args):
    return entry_point, None


if __name__ == '__main__':
    entry_point(sys.argv)
