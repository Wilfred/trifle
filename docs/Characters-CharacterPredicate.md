# character?

`(character? VALUE)`

The function `character?` returns `#true` if VALUE is a character, and
`#false` otherwise.

Examples:

```lisp
> (character? 'a')
#true

> (character? "foo")
#false

> (character? (list))
#false

> (character? #null)
#false
```
