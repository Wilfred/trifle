all: baobab

pypy-2.1-src.tar.bz2:
	wget https://bitbucket.org/pypy/pypy/downloads/pypy-2.1-src.tar.bz2

pypy: pypy-2.1-src.tar.bz2
	bunzip2 --keep pypy-2.1-src.tar.bz2
	tar -xf pypy-2.1-src.tar
	rm pypy-2.1-src.tar
	mv pypy-2.1-src pypy

baobab: pypy
	./rpython lexer.py
	mv lexer-c baobab

clean:
	rm -f pypy-2.1-src.tar.bz2
	rm -rf pypy
