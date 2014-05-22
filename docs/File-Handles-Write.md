# write!

`(write! HANDLE BYTES)`

The function `write!` writes BYTES to the file HANDLE. HANDLE must be
opened for writing.

Examples:

```lisp
> (set! h (open "/tmp/test.txt" :write))
#null
> (write! h (encode "hello world"))
#null
> (close! h)
#null
```

This will create (or overwrite if it already exists) a file
/tmp/test.txt with the contents `hello world`.

Note that repeatedly calling `write!` just appends to the file.

Example:

```lisp
> (set! h (open "/tmp/test.txt" :write))
#null
> (write! h (encode "trifle"))
#null
> (write! h (encode "!"))
#null
> (close! h)
#null
```

After running this code, /tmp/test.txt contains the text `trifle!`.
