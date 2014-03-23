# or

`(or EXPRESSION...)`

The macro `or` evaluates each of the EXPRESSIONS in turn
(left-to-right). If any are truthy, a truthy value is returned
immediately (without evaluating the remaining arguments). Otherwise, the
final falsey value is returned.

Examples:

```lisp
> (or #true #true)
#true

> (or #true #null)
#true

> (or #true (print! "I won't be printed."))
#true
```
