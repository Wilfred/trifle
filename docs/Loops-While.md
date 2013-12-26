# while

`(while CONDITION EXPRESSION...)`

The special expression `while` takes a condition and a variable number
of EXPRESSIONS. It evaluates the EXPRESSIONS if CONDITION
evaluates to a truthy value, then repeats until CONDITION
evaluates to a falsey value.

Always returns `null`.

Examples:

```lisp
> (let (i 1 total 0)
    (while (< i 11)
        (set! total (+ total i))
        (set! i (+ i 1)) ;; todo: use inc!
    )
    total
  )
55
```
