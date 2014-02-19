# inc!

`(inc! SYMBOL)`

The macro `inc!` updates the variable SYMBOL to be one higher than it
was before.

Examples:

```lisp
> (set! x 3)
#null
> (inc! x)
#null
> x
4
```
