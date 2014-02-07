# close!

`(close! HANDLE)`

The function `close!` closes the file handle given.

Examples:

```lisp
> (set! h (open "/tmp/testfile.txt" :write))
null
> (close! h)
null
```

You should close file handles when you are finished with them. When
your program terminates, your file handles are closed
automatically. However, you may run out of file handles if your
program runs for a long time.
