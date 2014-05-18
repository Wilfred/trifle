# try

`(try EXPRESSION :catch ERROR-TYPE SYMBOL CATCH-EXPRESSION)`

The special expression `try` evaluates EXPRESSION. If an exception is
raised during execution, the error is compared with ERROR-TYPE. If it
matches, CATCH-EXPRESSION is evaluated with the exception bound to
SYMBOL.

Note that SYMBOL is only bound inside CATCH-EXPRESSION, but any new
assignments will affect the function scope (i.e. the same as `let`).

If the error raised does not match ERROR, it propagates up the stack
until another `try` expression is found, otherwise the program
terminates.

Examples:

```lisp
> (try
  (/ 1 0)
  :catch zero-division-error e
  #null
)
#null
```
