# get-items

`(get-items HASHMAP)`

The function `get-items` returns all the key-value pairs in HASHMAP.

Note that hashmaps are not ordered, so the pairs may come back in any
order.

Examples:

```lisp
> (get-items {1 "foo", 2 "bar"})
((1 "foo") (2 "bar"))
```
