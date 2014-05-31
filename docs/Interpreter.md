# Interpreter

The Trifle interpreter is a program you run from the command line.

The Trifle source code includes a program `shell.tfl` that gives you
an interactive shell.

```
$ ./trifle shell.tfl
Trifle 0.9. Type (exit!) to quit.

> (+ 2 3)
5
```

You can run programs directly by passing the `-i` flag.

```
$ ./trifle -i '(+ 2 3)'
5

```

For longer programs, you can pass the filename as an argument.

```
$ echo '(print! (+ 2 3))' > add.tfl
$ ./trifle add.tfl
5
```
