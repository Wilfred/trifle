# same?

`(same VALUE VALUE)`

The function `same?` returns `true` if both arguments are of the same
type and represent the same value.

Examples:

```lisp
> (same? 1 1)
true

> (same? 1 2)
false

> (same? false 123)
false
```

Note that `same?` implements shallow equality, so lists with the same
elements are not the same. If two variables reference the same list
instance, `same?` will return `true`.

Examples:

```lisp
> (same? (list 1) (list 1))
false

> (set! x (list 1))
null
> (set! y x)
> (same? x y)
true
```
