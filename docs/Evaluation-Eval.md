# eval

`(eval EXPRESSION)`

The special expression `eval` evaluates EXPRESSION, then returns the
result of evaluating that result.

Examples:

```lisp
> (eval (parse "(+ 1 2)"))
3
> (eval (quote (* 2 3)))
6
```
