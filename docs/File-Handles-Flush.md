# flush!

`(flush! HANDLE)`

The function `flush!` flushes the internal buffer of HANDLE. Note that
data may not actually be written to disk until fsync.

HANDLE must be opened for writing.

Examples:

```lisp
> (set! h (open "/tmp/test.txt" :write))
#null
> (write! h (encode "hello world"))
#null
> (flush! h)
#null
```
