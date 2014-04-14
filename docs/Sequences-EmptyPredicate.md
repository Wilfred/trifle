# empty?

`(empty? SEQUENCE)`

The function `empty?` returns `#true` if SEQUENCE contains no
elements, and `#false` otherwise.

Examples:

```lisp
> (empty? "foo")
#false

> (empty? "")
#true

> (empty? (list 1))
#false

> (empty? (list))
#true
```
