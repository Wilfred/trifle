# get-key

`(get-key HASHMAP KEY)`

The function `get-key` gets the value in HASHMAP with key KEY. It
raises `missing_key` if KEY is not in HASHMAP.

Examples:

```lisp
> (get-key {1 "foo", 2 "bar"} 2)
"bar"
```
