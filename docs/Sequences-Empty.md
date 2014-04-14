# empty

`(empty SEQUENCE)`

The function `empty` returns a new empty sequence with the same type as
SEQUENCE. It's particularly useful when writing recursive functions.

Examples:

```lisp
> (empty "foo")
""

> (empty "")
""

> (empty (list 1))
()
```
