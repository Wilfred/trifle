# fresh-symbol

`(fresh-symbol)`

The function `fresh-symbol` returns a symbol that is guaranteed to be
different to all symbols in the current program. Each call to
`fresh-symbol` returns a unique symbol.

`fresh-symbol` is primarily intended for macros.

Examples:

```lisp
> (fresh-symbol)
1-unnamed
```
