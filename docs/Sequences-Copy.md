# copy

`(copy SEQUENCE)`

The function `copy` returns a copy of SEQUENCE.

```lisp
> (copy (list 1 2 3))
(1 2 3)
```

The result is `equal?` to the input, but not `same?`. The result may
therefore be modified without changing the original result.

```lisp
> (set! x (list 1))
#null
> (set! y (copy x))
#null
> (append! y 2)
#null
> x
(1)
> y
(1 2)
```

This is a shallow copy, so the values in SEQUENCES are shared with the
copy.

```lisp
> (set! x (list (list)))
#null
> (set! y (copy x))
#null
> (append! (first x) 1)
#null
> x
((1))
> y
((1))
```

