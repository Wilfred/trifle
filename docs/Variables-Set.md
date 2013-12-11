# set!

`(set! SYMBOL VALUE)`

The macro `set!` evaluates VALUE and assigns the result to SYMBOL in
the current scope. `set!` always returns `null`.

Examples:

    > (set! bananas 5)
    null
    > bananas
    5
