all: trifle

PYPY_VERSION=2.5.1

pypy-src.tar.bz2:
	wget https://bitbucket.org/pypy/pypy/downloads/pypy-$(PYPY_VERSION)-src.tar.bz2 -O pypy-src.tar.bz2

pypy: pypy-src.tar.bz2
	bunzip2 --keep pypy-src.tar.bz2
	tar -xf pypy-src.tar
	rm pypy-src.tar
	mv pypy-$(PYPY_VERSION)-src pypy

trifle: pypy $(wildcard interpreter/*.py)
	./rpython main.py
	mv main-c trifle

install:
	cp trifle /usr/local/bin/trifle

uninstall:
	rm /usr/local/bin/trifle

.PHONY: clean

clean:
	rm -f pypy-src.tar.bz2
	rm -rf pypy
	rm -f trifle
