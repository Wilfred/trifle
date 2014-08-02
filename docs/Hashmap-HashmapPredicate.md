# hashmap?

`(hashmap? VALUE)`

The function `hashmap?` returns `#true` if VALUE is a hashmap, and `#false`
otherwise.

Examples:

```lisp
> (hashmap? {})
#true

> (hashmap? #null)
#false
```
