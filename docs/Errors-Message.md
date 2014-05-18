# message

`(message EXCEPTION)`

The function `message` returns the message associated with exception
EXCEPTION.

Example:

```
> (try
    (throw error "hello world")
    :catch error e
    (message e)
)
"hello world"
```
