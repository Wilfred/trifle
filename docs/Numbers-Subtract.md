# -

`(- NUMBER...)`

The function `-` performs subtraction on a variable number of
arguments. It returns 0 if no arguments are provided.

If any arguments provided are floats, then `-` will return a
float. Otherwise, it will return an integer.

Examples:

```lisp
> (- 10 1)
9

> (- 10.0 1)
9.0

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
