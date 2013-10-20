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
./baobab -i <code snippet>
./baobab <path to script>"""
    return 1
        


def target(*args):
    return entry_point, None


if __name__ == '__main__':
    entry_point(sys.argv)
