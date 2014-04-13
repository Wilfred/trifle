# *

`(* NUMBER...)`

The function `*` performs multiplication on a variable number of
arguments. It returns 1 if no arguments are provided.

Examples:

```lisp
> (* 3 4)
12

> (*)
1
```

`*` will coerce integers to fractions, and fractions to floats, if
necessary.

```lisp
> (* 3 4.0)
12.0

> (* 1 1/2)
1/2

> (* 3.0 1/2)
1.5
```
