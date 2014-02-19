# set-symbol!

`(set-symbol! SYMBOL VALUE)`

The function `set-symbol!` assigns the variable SYMBOL to the value
VALUE. `set-symbol!` always returns `#null`. 

`set-symbol!` is primarily intended for metaprogramming. You will
usually want to use [set!](Variables-Set.md).

`set-symbol!` raises an error if SYMBOL-VALUE does not evaluate to a
symbol.

Examples:

    > (set-symbol! (quote bananas) 5)
    #null
    > bananas
    5
