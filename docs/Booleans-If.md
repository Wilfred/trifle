# if

`(if CONDITION THEN)`
`(if CONDITION THEN ELSE)`

The macro `if` takes two or three arguments. If the condition
evaluates to a [truthy](Booleans-Truthy.md) value, the THEN expression is
evaluated and returned. Otherwise, the ELSE expression is evaluated
and returned.

If no ELSE expression is given, `if` returns `null`.

Examples:

    > (if true 1 2)
    1

    > (if false 1 2)
    2

    > (if (quote (foo)) 1 2)
    1

    > (if false 1)
    null
