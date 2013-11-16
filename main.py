import sys
import os

from lexer import lex
from parser import parse


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


def read_line(prefix):
    """Equivalent to raw_input, which isn't available on RPython."""
    sys.stdout.write(prefix)
    return sys.stdin.readline()[:-1] # discard the trailing last newline


def entry_point(argv):
    """Either a file name:
    $ ./baobab ~/files/foo.bao

    A code snippet:
    $ ./baobab -i '1 2'

    Or a REPL:
    $ ./baobob

    """
    if len(argv) == 1:
        # REPL. Ultimately we will rewrite this as a Baobab program.
        print "Baobab 0.1 interpreter. Press Ctrl-C to exit."
        while True:
            try:
                user_input = read_line('> ')
                lexed_tokens = lex(user_input)
                parse_tree = parse(lexed_tokens)
                print parse_tree.as_string()
            except KeyboardInterrupt:
                print
                return 0
    
    elif len(argv) == 2:
        # open the file
        filename = argv[1]

        if not os.path.exists(filename):
            print 'No such file: %s' % filename
            return 2
        
        code = get_contents(filename)
        lexed_tokens = lex(code)
        parse_tree = parse(lexed_tokens)
        
        print "parse tree:" % parse_tree.as_string()
        return 0
    
    elif len(argv) == 3:
        if argv[1] == '-i':
            code_snippet = argv[2]
            lexed_tokens = lex(code_snippet)
            parse_tree = parse(lexed_tokens)

            print "parse tree: %s" % parse_tree.as_string()
            return 0
            
    print """Usage:
./baobab
./baobab -i <code snippet>
./baobab <path to script>"""
    return 1
        


def target(*args):
    return entry_point, None


if __name__ == '__main__':
    entry_point(sys.argv)
