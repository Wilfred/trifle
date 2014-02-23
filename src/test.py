import sys


def entry_point(argv):
    try:
        f = open("/tmp/test.txt", 'r')
        print "f: %s" % f.read()
    except IOError as e:
        if e.errno == 2:
            print 'yikes'
        pass

    return 0


def target(*args):
    return entry_point, None


if __name__ == '__main__':
    entry_point(sys.argv)
