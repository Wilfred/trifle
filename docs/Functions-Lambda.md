# lambda

`(lambda SYMBOLS EXPRESSION...)`

The special expression `lambda` defines an anonymous function. When a
lambda expression is evaluated, the arguments given are set as
variables, and the expressions are evaluated in that environment.

`lambda` raises an error if it is given too few arguments, or if
SYMBOLS is not a list of symbols.

Examples:

```lisp
> ((lambda (x) (+ x 1)) 5)
6
```
