# function

`(function SYMBOL PARAMETERS EXPRESSIONS...)`

The macro `function` defines a named function. PARAMETERS and
EXPRESSIONS are passed to [lambda](Functions-Lambda.md).

Examples:

```lisp
> (function double (x) (* x 2))
null
> (double 4)
8
```
