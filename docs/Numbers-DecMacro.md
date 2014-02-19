# dec!

`(dec! SYMBOL)`

The macro `dec!` updates the variable SYMBOL to be one lower than it
was before.

Examples:

```lisp
> (set! x 3)
#null
> (dec! x)
#null
> x
2
```
