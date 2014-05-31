# exception-type

`(exception-type EXCEPTION)`

The function `exception-type` returns the exception type associated with exception
EXCEPTION.

Example:

```
> (try
    (throw error "hello world")
    :catch error e
    (exception-type e)
)
#error(no-such-variable)
```
