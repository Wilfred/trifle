# and

`(and EXPRESSION...)`

The macro `and` evaluates each of the EXPRESSIONS in turn
(left-to-right). If any are `#false`, `#false` is returned
immediately (without evaluating the remaining arguments). Otherwise,
returns `#true`.

Examples:

```lisp
> (and #true #true)
#true

> (and #true #false)
#false

> (and #false (print! "I won't be printed."))
#false
```
