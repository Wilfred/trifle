# unless

`(unless CONDITION EXPRESSION...)`

`unless` evaluates CONDITION, and if the condition is not truthy, it evaluates all
the other EXPRESSIONs given and returns the value of the last one.

Examples:

```lisp
> (set! x 50)
#null
> (unless (< x 10)
  (print! "x is pretty big!")
  5
)
x is pretty big!
5
```
