# encode

`(encode STRING)`

The function `encode` takes a string and returns the equivalent bytes
of that string encoded with UTF-8.

Examples:

```lisp
> (encode "soufflé")
#bytes("souffl\xc3\xa9")

```
