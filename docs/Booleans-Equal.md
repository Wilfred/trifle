# equal?

`(equal? VALUE VALUE)`

The function `equal?` returns `true` if both arguments represent the
same value.

Examples:

```lisp
> (equal? 2 (+ 1 1))
true

> (equal? (list 1) (list 1))
true

> (equal? (list 1) (list 1 2))
false

> (equal? null "banana")
false
```

`equal?` can compare floats to their equivalent integers:

Examples:

```lisp
> (equal? 1 1.0)
true
```
