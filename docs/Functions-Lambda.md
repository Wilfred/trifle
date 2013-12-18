# lambda

`(lambda PARAMETERS EXPRESSION...)`

The special expression `lambda` defines an anonymous function. When a
lambda expression is evaluated, the arguments given are set as
variables according to the parameters, and the expressions are
evaluated in that environment.

`lambda` raises an error if it is given too few arguments, or if
PARAMETERS is not a list of symbols.

Examples:

```lisp
> ((lambda (x) (+ x 1)) 5)
6
```

Parameters may also contain the keyword `:rest` to signify a parameter
that takes all the remaining arguments to the lambda.

Example:

```lisp
> ((lambda (x y :rest z) 1 2 3 4 5)
(3 4 5)
```
