# append!

`(append! SEQUENCE VALUE)`

The function `append!` inserts VALUE as the last item in SEQUENCE.

Examples:

```lisp
> (set! my-list (list 20 30))
#null
> (append! my-list 40)
#null
> my-list
(20 30 40)

> (set! my-bytes #bytes("ab"))
#null
> (append! my-bytes 99)
#null
> my-bytes
#bytes("abc")

> (set! my-string "ab")
#null
> (append! my-string 'c')
#null
> my-string
"abc"
```
