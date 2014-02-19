# set-index!

`(set-index! SEQUENCE INDEX VALUE)`

The function `set-index!` sets the item at position INDEX in SEQUENCE to
VALUE. It raises an error if INDEX is out of bounds. For an n-item
sequence, INDEX must be between -n and n-1 (inclusive).

Examples:

```lisp
> (set! my-list (list 10 20 30))
#null
> (set-index! my-list 0 11)
#null
> my-list
(11 20 30)
> (set-index! my-list -1 100)
#null
> my-list
(11 20 100)
```

When used with bytestrings, VALUE must be an integer between 0 and
255.

Example:

```lisp
> (set! my-bytestring #bytes("bbc"))
#null
> (set-index! my-bytestring 0 97)
#null
> my-bytestring
#bytes("abc")
```
