all: baobab

PYPY_VERSION=2.2

pypy-src.tar.bz2:
	wget https://bitbucket.org/pypy/pypy/downloads/pypy-$(PYPY_VERSION)-src.tar.bz2 -O pypy-src.tar.bz2

pypy: pypy-src.tar.bz2
	bunzip2 --keep pypy-$(PYPY_VERSION)-src.tar.bz2
	tar -xf pypy-$(PYPY_VERSION)-src.tar
	rm pypy-$(PYPY_VERSION)-src.tar
	mv pypy-$(PYPY_VERSION)-src pypy

baobab: pypy main.py
	./rpython main.py
	mv main-c baobab

clean:
	rm -f pypy-src.tar.bz2
	rm -rf pypy
