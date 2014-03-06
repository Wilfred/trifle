# list?

`(list? VALUE)`

The function `list?` returns `#true` if VALUE is a list, and `#false`
otherwise.

Examples:

```lisp
> (list? (list))
#true

> (list? #null)
#false

> (list? #bytes("abc"))
#false
```
