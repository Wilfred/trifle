# not

`(not VALUE)`

The function `not` returns `#true` if VALUE is not
[truthy](Booleans-Truthy.md), and `false otherwise.

Examples:

```lisp
> (not #true)
#false

> (not #false)
#true

> (not (list))
#true
```
