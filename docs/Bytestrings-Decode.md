# decode

`(decode BYTES)`

The function `decode` takes a bytes and returns the equivalent string,
assuming BYTES is UTF-8 encoded.

Examples:

```lisp
> (decode #bytes("souffl\xc3\xa9"))
"soufflé"
```
