# set-item!

`(set-item! LIST INDEX VALUE)`

The function `set-item!` sets the item at position INDEX in LIST to
VALUE. It raises an error if INDEX is out of bounds.

Examples:

```lisp
> (set! my-list (list 10 20 30))
null
> (set-item! my-list 0 11)
null
> my-list
(11 20 30)
```
