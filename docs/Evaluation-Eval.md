# eval

`(eval EXPRESSION)`

The function `eval` returns the result of evaluating EXPRESSION.

Examples:

```lisp
> (eval (parse "(+ 1 2)"))
3
> (eval (quote (* 2 3)))
6
```
