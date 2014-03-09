# push!

`(push! SEQUENCE VALUE)`

The function `push!` inserts VALUE as the first item in SEQUENCE.

Examples:

```lisp
> (set! my-list (list 20 30))
#null
> (push! my-list 10)
#null
> my-list
(10 20 30)

> (set! my-string "bc")
#null
> (push! my-string 'a')
#null
> my-string
"abc"

> (set! my-bytes #bytes("bc"))
#null
> (push! my-bytes 97)
#null
> my-bytes
#bytes("abc")
```
