# if

`(if CONDITION THEN ELSE)`

The special expression `if` takes two three arguments. If the
condition evaluates to `#true`, the THEN expression is evaluated and
returned. Otherwise, the ELSE expression is evaluated and returned.

Examples:

    > (if #true 1 2)
    1

    > (if #false 1 2)
    2

    > (if (equal? "a" "b") 1 2)
    1
