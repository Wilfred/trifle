# string?

`(string? VALUE)`

The function `string?` returns `#true` if VALUE is a string, and
`#false` otherwise.

Examples:

```lisp
> (string? "foo")
#true

> (string? (list))
#false

> (string? #null)
#false

> (string? #bytes("abc"))
#false
```
