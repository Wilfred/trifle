# filter

`(filter FUNCTION SEQUENCE)`

The function `filter` returns a sequence containing all the elements
in SEQUENCE where `(FUNCTION element)` is truthy.

Examples:

```lisp
> (filter (lambda (x) (> x 2)) (list 1 2 3 4))
(3 4)
```
