# for-each

`(for-each SYMBOL SEQUENCE EXPRESSION...)`

The macro `for-each` evaluates EXPRESSIONS repeatedly, once for each
value in SEQUENCE. In each iteration, SYMBOL is set to the next value in
SEQUENCE.

Returns `#null`.

Examples:

```lisp
> (let (total 0 numbers (list 1 2 3 4))
    (for-each number numbers
      (set! total (+ total number))
    )
    total
  )
10
```
