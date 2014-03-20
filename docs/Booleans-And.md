# and

`(and EXPRESSION...)`

The macro `and` evaluates each of the EXPRESSIONS in turn
(left-to-right). If any are falsey, a falsey value is
returned. Otherwise, a truthy value is returned.

Examples:

```lisp
> (and #true #true)
#true

> (and #true #false)
#false

> (and #false (print! "I won't be printed."))
#false
```
