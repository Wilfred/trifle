# throw

`(throw EXCEPTION-TYPE MESSAGE)`

The function `throw` throws an exception of type EXCEPTION-TYPE with
message MESSAGE. It should be caught with `try`.

Examples:

```lisp
> (try (throw error "something went wrong!")
    :catch error e
    (print! "caught the error!")
caught the error!
#null
```
