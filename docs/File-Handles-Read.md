# read

`(read HANDLE)`

The function `read` reads all the bytes in the file from the current
file and returns a bytes sequence.

Examples:

This example assumes you have a text file with a UTF-8 encoding at /tmp/test.txt. You
can create one from bash with:

```bash
$ echo -n 'a delicious soufflé and a spoon' > /tmp/test.txt
```

You can now try this Trifle code:

```lisp
> (set! h (open "/tmp/test.txt" :read))
#null
> (read h)
#bytes("a delicous souffl\xc3\xa9 and a spoon")
```
