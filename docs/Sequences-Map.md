# map

`(map FUNCTION SEQUENCE)`

The function `map` calls FUNCTION with every value in SEQUENCE, and builds
a new sequence of the results.

Examples:

```lisp
> (map (lambda (x) (* x 2)) (list 1 2 3))
(2 4 6)

> (map inc #bytes("abc"))
#bytes("bcd")
```
