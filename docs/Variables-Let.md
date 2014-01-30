# let

`(let BINDINGS EXPRESSIONS...)`

The special expression `let` introduces a new scope with additional
variables, then evaluates EXPRESSIONS with that new scope. BINDINGS is
a list with an odd number of items
`SYMBOL EXPRESSION SYMBOL EXPRESSION...`.

Examples:

    > (let (x 1) (+ x 1))
    2
    > (set! y 0) (let (y 1) (set! y 2)) y
    0

## Undefined variables

Note that using `let` does not capture any variables other than those
in BINDINGS.

    > (let (x 0) (set! y 1)) y
    1

In this example, `y` is defined as a global variable, and persists
outside the `let`.
