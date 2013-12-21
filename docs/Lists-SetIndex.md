# set-index!

`(set-index! LIST INDEX VALUE)`

The function `set-index!` sets the item at position INDEX in LIST to
VALUE. It raises an error if INDEX is out of bounds.

Examples:

```lisp
> (set! my-list (list 10 20 30))
null
> (set-index! my-list 0 11)
null
> my-list
(11 20 30)
```
