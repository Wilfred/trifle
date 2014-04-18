# when-not

`(when-not CONDITION EXPRESSION...)`

`when-not` evaluates CONDITION, and if the result is `#false`, it
evaluates all the other EXPRESSIONs given and returns the value of the
last one. Otherwise, it returns `#null`.

Examples:

```lisp
> (when-not (equal? 5 10)
    (print! "5 is not equal to 10!")
    "a string"
  )
5 is not equal to 10!
5
> (when-not #true 1)
#null
```
