# append!

`(append! LIST VALUE)`

The function `append!` inserts VALUE as the last item in LIST.

Examples:

```lisp
> (set! my-list (list 20 30))
null
> (append! my-list 40)
null
> my-list
(20 30 40)
```
