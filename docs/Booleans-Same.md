# same?

`(same? VALUE VALUE)`

The function `same?` returns `true` if both arguments are the same
value. Note this is different from `equal?`, which compares if two
values are equivalent.

Examples:

```lisp
> (same? (quote a) (quote a))
true

> (same? false 123)
false
```

If two values are `same?`, then they are the same value in memory. For
example, lists with the same elements are not the same. If two
variables reference the same list instance, `same?` will return
`true`.

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
