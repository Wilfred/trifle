# map

`(map FUNCTION LIST)`

The function `map` calls FUNCTION with every value in LIST, and builds
a new list of the results.

Examples:

```lisp
> (map (lambda (x) (* x 2)) (list 1 2 3))
(2 4 6)
```
