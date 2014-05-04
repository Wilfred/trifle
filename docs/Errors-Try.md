# try

`(try EXPRESSION :catch (ERROR EXPRESSION...))`

The special expression `try` evaluates EXPRESSION. If an exception is
raised during execution, the error is compared with ERROR. If it
matches, the EXPRESSION after ERROR is evaluated and returned.

If the error raised does not match ERROR, it propagates up the stack
until another `try` expression is found, otherwise the program
terminates.

Examples:

```lisp
(try
  (/ 1 0)
  :catch (zero-division-error #null)
)
```
