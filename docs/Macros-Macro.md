# macro

`(macro NAME PARAMETERS EXPRESSION...)`

The special form `macro` defines a macro in the global scope (even if
called inside a function). A macro is given its arguments unevaluated,
and returns an expression for the interpreter to evaluate.

Examples:

```lisp
> (macro unless (condition expression)
      (quote (if (not (unquote condition)) (unquote expression)))
  )
> (unless true foo) ; no error thrown, since foo is not evaluated
```
