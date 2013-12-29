# push!

`(push! LIST VALUE)`

The function `push!` inserts VALUE as the first item in LIST.

Examples:

```lisp
> (set! my-list (list 20 30))
null
> (push! my-list 10)
null
> my-list
(10 20 30)
```
