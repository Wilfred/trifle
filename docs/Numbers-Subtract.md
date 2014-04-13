# -

`(- NUMBER...)`

The function `-` performs subtraction on a variable number of
arguments. It returns 0 if no arguments are provided.

Examples:

```lisp
> (- 10 1)
9

> (-)
0
```

If a single argument is given, `-` negates it.

Examples:

```lisp
> (- 2)
-2

> (- -2)
2
```

`-` will coerce integers to fractions, and fractions to floats, if
necessary.

```lisp
> (- 10.0 1)
9.0

> (- 5/2 1)
3/2
```
