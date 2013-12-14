# Building

The Trifle lisp interpreter is written in RPython, a statically typed
subset of Python.

Building the interpreter is simply a matter of:

```bash
$ cd src
$ make
```

This will create a `trifle` binary in your current directory.

Since RPython is a subset of Python, you can run the interpreter
without compiling. This is slower, but very useful for testing.

```bash
$ cd src
$ ./trifle_cpython
```

The tests are written in normal Python, making inspecting unexpected
results and errors easier. You can run the tests with:

```bash
$ cd src
$ ./run_tests
```
