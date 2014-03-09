# decode

`(decode BYTESTRING)`

The function `decode` takes a bytestring and returns the equivalent
string, assuming BYTESTRING is UTF-8 encoded.

Examples:

```lisp
> (decode #bytes("souffl\xc3\xa9"))
"soufflé"
```
