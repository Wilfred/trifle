# set-key!

`(set-key! HASHMAP)`

The function `set-key!` returns all the key-value pairs in HASHMAP.

Note that hashmaps are not ordered, so the pairs may come back in any
order.

Examples:

```lisp
> (set! my-hashmap {1 "foo"})
#null
> (set-key! my-hashmap 1 "bar")
#null
> my-hashmap
{1 "bar"}
```
