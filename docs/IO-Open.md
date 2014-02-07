# open

`(open PATH FLAG)`

The function `open` opens the file at PATH and returns a file
handle. FLAG can take the value `:read` or `:write`.

Examples:

```lisp
> (open "/tmp/testfile.txt" :write)
#file-handle("/tmp/foo.txt")

> (open "/etc/hosts" :read)
#file-handle("/etc/hosts")
```
