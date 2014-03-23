# and

`(and EXPRESSION...)`

The macro `and` evaluates each of the EXPRESSIONS in turn
(left-to-right). If any are falsey, a falsey value is returned
immediately (without evaluating the remaining arguments). Otherwise, the
final truthy value is returned.

Examples:

```lisp
> (and #true #true)
#true

> (and #true #false)
#false

> (and #false (print! "I won't be printed."))
#false
```
