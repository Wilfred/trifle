# bytestring?

`(bytestring? VALUE)`

The function `bytestring?` returns `#true` if VALUE is a bytestring, and
`#false` otherwise.

Examples:

```lisp
> (bytestring? #bytes("abc"))
#false

> (bytestring? "foo")
#false

> (bytestring? (list))
#false

> (bytestring? #null)
#false
```
