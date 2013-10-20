import sys
import os

# Sadly, re isn't available in rpython.
from rpython.rlib.rsre import rsre_core
from rpython.rlib.rsre.rpy import get_code


WHITESPACE = 'whitespace'
COMMENT = 'comment'
OPEN_PAREN = 'open-paren'
CLOSE_PAREN = 'close-paren'
INTEGER = 'integer'
SYMBOL = 'symbol'


TOKENS = {
    WHITESPACE: get_code(r"\s+"),
    COMMENT: get_code(";[^\n]*"),
    OPEN_PAREN: get_code(r"\("),
    CLOSE_PAREN: get_code(r"\)"),

    # todo: it'd be nice to allow number literals with underscores,
    # e.g. 1_000_000
    INTEGER: get_code('[1-9][0-9]*'),

    SYMBOL: get_code('[a-z*/+-]+'),
}


def lex(text):
    lexed_tokens = []

    while True:
        found_match = False
    
        for token, regexp in TOKENS.iteritems():
            match = rsre_core.match(regexp, text)
            if match:
                found_match = True

                if token not in [WHITESPACE, COMMENT]:
                    lexed_tokens.append((token, text[:match.match_end]))
                
                text = text[match.match_end:]
                break

        if not text:
            # successfully lexed everything
            break

        if not found_match:
            print "Could not lex remainder: '%s'" % text
            break

    return lexed_tokens

def get_contents(filename):
    # todo: programs should be UTF-8 only
    fp = os.open(filename, os.O_RDONLY, 0777)

    program_contents = ""
    while True:
        read = os.read(fp, 4096)
        if len(read) == 0:
            break
        program_contents += read
    os.close(fp)

    return program_contents


def entry_point(argv):
    """We support either a filename or inline code passed with -i.

    $ ./lexer-c ~/files/foo.bao
    $ ./lexer-c -i '1 2'

    """
    if len(argv) == 2:
        # open the file
        filename = argv[1]

        if not os.path.exists(filename):
            print 'No such file: %s' % filename
            return 2
        
        code = get_contents(filename)
        lexed_tokens = lex(code)
        
        print "tokens: %s" % lexed_tokens
        return 0
    
    elif len(argv) == 3:
        if argv[1] == '-i':
            code_snippet = argv[2]
            lexed_tokens = lex(code_snippet)

            print "tokens: %s" % lexed_tokens
            return 0
            
    print """Usage:
./baobab -i <code snippet>
./baobab <path to script>"""
    return 1
        


def target(*args):
    return entry_point, None


if __name__ == '__main__':
    entry_point(sys.argv)
