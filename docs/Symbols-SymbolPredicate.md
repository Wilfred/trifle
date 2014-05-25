# symbol?

`(symbol? VALUE)`

The function `symbol?` returns `#true` if VALUE is a symbol, and `#false`
otherwise.

Examples:

```lisp
> (symbol? (quote x))
#true

> (symbol? (quote (x))
#false

> (symbol? 1)
#false
```
