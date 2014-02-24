# zero?

`(zero? VALUE)`

The function `zero?` returns `#true` if the value given is zero, and
`#false` otherwise.

Examples:

```lisp
> (zero? 0)
#true
> (zero? 1)
#false

; Floating point is fine too.
> (zero? 0.0)
#true
> (zero? -0.0)
#true

; If it's not a number, zero? returns false.
> (zero? (list 0))
#false
> (zero? #null)
#false
```
