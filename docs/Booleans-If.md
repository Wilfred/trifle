# if

`(if CONDITION THEN)`
`(if CONDITION THEN ELSE)`

The special expression `if` takes two or three arguments. If the
condition evaluates to `#true`, the THEN
expression is evaluated and returned. Otherwise, the ELSE expression
is evaluated and returned.

If no ELSE expression is given and CONDITION is `#false`, `if` returns
`#null`.

Examples:

    > (if #true 1 2)
    1

    > (if #false 1 2)
    2

    > (if (equal? "a" "b") 1 2)
    1

    > (if #false 1)
    #null
