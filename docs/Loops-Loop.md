# for-each

`(loop EXPRESSION...)`

The macro `loop` evaluates EXPRESSIONS repeatedly, in an infinite loop.

Examples:

```lisp
> (let (x 0)
    (try
       (loop
         (if (< x 5)
           (inc! x)
           (throw value-error "Done!")
         )
       )
       :except value-error e
       x
     )
   )
5
```
