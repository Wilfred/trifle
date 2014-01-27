# get-index

`(get-index LIST INDEX)`

The function `get-index` gets the item at position INDEX in LIST. It
raises an error if INDEX is out of bounds. For an n-item list, INDEX
must be between -n and n-1 (inclusive).

Examples:

```lisp
> (get-index (list 10 20 30) 0)
10
> (get-index (list 10 20 30) -1)
30
```

