# /

`(/ NUMBER NUMBER...)`

The function `/` performs division on two or more arguments.

For integers and fractions, the result is a fraction:

```lisp
> (/ 1 2)
1/2

> (/ 1/2 3)
1/6

> (/ 1 2 2)
1/4
```

If floats are used, `/` will coerce all its arguments to floats and
perform floating point division:

```lisp
> (/ 0.5 1/4)
2.0
```
