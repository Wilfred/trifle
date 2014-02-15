# decode

`(decode BYTES)`

The function `decode` takes a bytes and returns the equivalent string,
assuming BYTES is UTF-8 encoded.

Examples:

```lisp
> x
#bytes("souffl\xc3\xa9")
> (decode x)
"soufflé"
```
