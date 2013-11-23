all: baobab

PYPY_VERSION=2.2

pypy-src.tar.bz2:
	wget https://bitbucket.org/pypy/pypy/downloads/pypy-$(PYPY_VERSION)-src.tar.bz2 -O pypy-src.tar.bz2

pypy: pypy-src.tar.bz2
	bunzip2 --keep pypy-src.tar.bz2
	tar -xf pypy-src.tar
	rm pypy-src.tar
	mv pypy-$(PYPY_VERSION)-src pypy

baobab: pypy main.py lexer.py baobab_types.py parser.py evaluator.py
	./rpython main.py
	mv main-c baobab

clean:
	rm -f pypy-src.tar.bz2
	rm -rf pypy
