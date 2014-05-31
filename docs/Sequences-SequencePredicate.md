# sequence?

`(sequence? VALUE)`

The function `sequence?` returns `#true` if VALUE is a sequence

Examples:

```lisp
> (sequence? "")
#true

> (sequence? (list 1))
#true

> (sequence? #null)
#false
```
