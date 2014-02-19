# set!

`(set! SYMBOL VALUE)`

The macro `set!` evaluates VALUE and assigns the result to SYMBOL in
the current scope. `set!` always returns `#null`.

`set!` raises an error if SYMBOL is not a symbol.

Examples:

    > (set! bananas 5)
    #null
    > bananas
    5
