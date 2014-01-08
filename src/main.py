import sys
import os

from rpython.rtyper.module.ll_os_environ import getenv_llimpl

from lexer import lex
from trifle_parser import parse
from evaluator import evaluate_all
from errors import TrifleError
from environment import fresh_environment
from almost_python import raw_input


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


def env_with_prelude():
    """Return a fresh environment where the prelude has already been
    evaluated.

    """
    # todo: document TRIFLEPATH
    # todo: should we inline the prelude, so changing TRIFLEPATH doens't break this?
    trifle_path = getenv_llimpl("TRIFLEPATH") or "."
    prelude_path = os.path.join(trifle_path, "prelude.tfl")
    
    # Trifle equivalent of PYTHONPATH.
    code = get_contents(prelude_path)
    lexed_tokens = lex(code)
    parse_tree = parse(lexed_tokens)

    env = fresh_environment()
    evaluate_all(parse_tree, env)

    return env


# todo: some unit tests to ensure the top level works
def entry_point(argv):
    """Either a file name:
    $ ./trifle ~/files/foo.bao

    A code snippet:
    $ ./trifle -i '1 2'

    Or a REPL:
    $ ./trifle

    """
    if len(argv) == 1:
        # REPL. Ultimately we will rewrite this as a Trifle program.
        print "Trifle interpreter. Press Ctrl-C to exit."

        env = env_with_prelude()
        while True:
            try:
                user_input = raw_input('> ')
                lexed_tokens = lex(user_input)
                parse_tree = parse(lexed_tokens)

                print evaluate_all(parse_tree, env).repr()
            except TrifleError as e:
                print "Error: %s" % e.message
            except KeyboardInterrupt:
                print
                return 0
    
    elif len(argv) == 2:
        # open the file
        filename = argv[1]

        if not os.path.exists(filename):
            print 'No such file: %s' % filename
            return 2

        env = env_with_prelude()
        code = get_contents(filename)
        lexed_tokens = lex(code)
        parse_tree = parse(lexed_tokens)
        try:
            print evaluate_all(parse_tree, env).repr()
        except TrifleError as e:
            print "Error: %s" % e.message
            return 1
        
        return 0
    
    elif len(argv) == 3:
        if argv[1] == '-i':
            env = env_with_prelude()
            code_snippet = argv[2]
            lexed_tokens = lex(code_snippet)
            parse_tree = parse(lexed_tokens)

            try:
                print evaluate_all(parse_tree, env).repr()
            except TrifleError as e:
                print "Error: %s" % e.message
                return 1
            return 0
            
    print """Usage:
./trifle
./trifle -i <code snippet>
./trifle <path to script>"""
    return 1
        


def target(*args):
    return entry_point, None


if __name__ == '__main__':
    entry_point(sys.argv)
