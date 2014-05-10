# case

`(case (CONDITION EXPRESSION...)...)`

`case` implements a case statement. Each CONDITION is evaluated in
order. If CONDITION evaluates to `#true`, EXPRESSION... is evaluated
and returned.

Examples:

```lisp
> (set! x 5)
#null
> (case
    ((zero? x) (print "x is zero!") 1)
    ((< x 10) (print "x is pretty small!") 2)
    (#true (print "x has some other value!") 3)
  )
x is pretty small!
2
```
