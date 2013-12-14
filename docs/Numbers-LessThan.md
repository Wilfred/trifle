# <

`(< NUMBER NUMBER...)`

The function `<` compares numbers, returning `true` if each argument
is less than the next argument.

`<` raises an error if any of its arguments are not numbers.

Examples:

    > (< 1 2)
    true

    > (< 1 5 6)
    true

    > (< 10 9)
    false

