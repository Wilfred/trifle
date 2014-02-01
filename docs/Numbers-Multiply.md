# *

`(* NUMBER...)`

The function `*` performs multiplication on a variable number of
arguments. It returns 1 if no arguments are provided.

If any arguments provided are floats, then `*` will return a
float. Otherwise, it will return an integer.

Examples:

```lisp
> (* 3 4)
12

> (* 3 4.0)
12.0

> (*)
1
```
