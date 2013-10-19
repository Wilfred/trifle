import sys


def entry_point(argv):
    print 'hello world'
    return 0


def target(*args):
    return entry_point, None


if __name__ == '__main__':
    entry_point(sys.argv)
