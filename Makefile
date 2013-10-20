all: pypy

pypy-2.1-src.tar.bz2:
	wget https://bitbucket.org/pypy/pypy/downloads/pypy-2.1-src.tar.bz2

pypy: pypy-2.1-src.tar.bz2
	bunzip2 --keep pypy-2.1-src.tar.bz2
	tar -xf pypy-2.1-src.tar
	rm pypy-2.1-src.tar
	mv pypy-2.1-src pypy

clean:
	rm -f pypy-2.1-src.tar.bz2
	rm -rf pypy
