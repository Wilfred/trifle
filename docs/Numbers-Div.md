# div

`(div INTEGER INTEGER)`

The function `div` performs integer division. Integer division always
rounds the result down (towards negative infinity) to the nearest
whole number.

`div` raises an error if the second argument is zero.

Examples:

```lisp
> (div 6 3)
2

> (div 5 2)
2

> (div -5 2)
-3
```
