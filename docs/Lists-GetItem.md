# get-item

`(get-item LIST INDEX)`

The function `get-item` gets the item at position INDEX in LIST. It
raises an error if INDEX is out of bounds.

Examples:

```lisp
> (get-item (list 10 20 30) 0)
10
```
