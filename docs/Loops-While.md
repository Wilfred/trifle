# while

`(while CONDITION EXPRESSION...)`

The special expression `while` takes a condition and a variable number
of EXPRESSIONS. It evaluates the EXPRESSIONS if CONDITION
evaluates to `#true`, then repeats until CONDITION
evaluates to `#false`.

Always returns `#null`.

Examples:

```lisp
> (let (i 1 total 0)
    ; Sum numbers from 1 to 10.
    (while (<= i 10)
        (set! total (+ total i))
        (inc! i)
    )
    total
  )
55
```
