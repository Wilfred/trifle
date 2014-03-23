# insert!

`(insert! SEQUENCE INDEX VALUE)`

The built-in function `insert!` inserts VALUE at INDEX in
SEQUENCE.

Examples:

```lisp
> (set! my-list (list 20 30))
#null
> (insert! my-list 1 40)
#null
> my-list
(20 40 30)

> (set! my-bytes #bytes("ab"))
#null
> (insert! my-bytes 2 99)
#null
> my-bytes
#bytes("abc")

> (set! my-string "ab")
#null
> (insert! my-string 2 'c')
#null
> my-string
"abc"
```
