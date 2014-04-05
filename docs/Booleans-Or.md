# or

`(or EXPRESSION...)`

The macro `or` evaluates each of the EXPRESSIONS in turn
(left-to-right). If any are `#true`, `#true` is returned immediately
(without evaluating the remaining arguments). Otherwise, returns `#false`.

Examples:

```lisp
> (or #true #true)
#true

> (or #true #false)
#true

> (or #true (print! "I won't be printed."))
#true
```
