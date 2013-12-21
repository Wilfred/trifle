# push!

`(push! LIST VALUE INDEX?)`

The function `push!` inserts VALUE in LIST. If INDEX is given, VALUE
is inserted before the item at INDEX. Otherwise, INDEX defaults to 0.

Examples:

```lisp
> (set! my-list (list 20 30))
null
> (push! my-list 10)
null
> my-list
(10 20 30)

> (push! my-list 15 1)
null
> my-list
(10 15 20 30)
```
