# rest

`(rest SEQUENCE)`

The function `rest` returns a copy of SEQUENCE with the first element
removed.

Examples:

```lisp
> (rest (list 1 2 3))
(2 3)
> (rest #bytes("abc"))
#bytes("bc")
```
