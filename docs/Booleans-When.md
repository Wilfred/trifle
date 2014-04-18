# when

`(when CONDITION EXPRESSION...)`

`when` evaluates CONDITION, and if the result is `#true`, it
evaluates all the other EXPRESSIONs given and returns the value of the
last one. Otherwise, it returns `#null`.

Examples:

```lisp
> (when (equal? 5 5)
    (print! "5 is equal to itself!")
    "a string"
  )
5 is equal to itself!
5
> (when #false 1)
#null
```
