# call

`(call VALUE LIST)`

The function `call` calls VALUE (which must be a function or macro)
with LIST as its arguments.

```lisp
> (call + (list 1 2))
3

> (set! x 1)
#null
> (call inc! (list (quote x)))
#null
> x
2
```
