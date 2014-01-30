# call

`(call FUNCTION LIST)`

The special expression `call` evaluates FUNCTION, evaluates LIST, then calls
FUNCTION with LIST as its arguments.

```lisp
> (call + (list 1 2))
3
```
