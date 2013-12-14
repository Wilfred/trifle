# Subtraction

`(- NUMBER...)`

The function `-` performs subtraction on a variable number of
arguments. It returns 0 if no arguments are provided.

`-` raises an error if any of its arguments are not numbers.

Examples:

    > (- 10 1)
    9

    > (-)
    0

If a single argument is given, `-` negates it.

Examples:

    > (- 2)
    -2
    
    > (- -2)
    2
