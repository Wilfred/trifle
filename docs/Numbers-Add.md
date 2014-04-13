# +

`(+ NUMBER...)`

The function `+` performs addition on a variable number of
arguments. It returns 0 if no arguments are provided.

`+` raises an error if any of its arguments are not numbers.

Examples:

```lisp
> (+ 1 2)
2

> (+ 1/2 1/3)
5/6

> (+)
0

> (+ 1)
1

```

`+` will coerce integers to fractions, and fractions to floats, if
necessary.

```lisp
> (+ 1 1/2)
3/2

> (+ 1.0 1/2)
1.5

> (+ 1 2.0)
3.0
```
