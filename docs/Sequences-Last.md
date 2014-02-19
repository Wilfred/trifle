# last

`(last SEQUENCE)`

The function `last` returns the first element in SEQUENCE. It raises
an error if SEQUENCE is empty.

Examples:

```lisp
> (last (list 1 2))
2
> (last #bytes("abc"))
99
```
