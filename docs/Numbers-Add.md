# +

`(+ NUMBER...)`

The function `+` performs addition on a variable number of
arguments. It returns 0 if no arguments are provided.

If any arguments provided are floats, then `+` will return a
float. Otherwise, it will return an integer.

`+` raises an error if any of its arguments are not numbers.

Examples:

```lisp
> (+ 1 2)
2

> (+)
0

> (+ 1)
1

> (+ 1 2.0)
3.0
```
