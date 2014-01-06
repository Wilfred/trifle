# set-symbol!

`(set-symbol! SYMBOL-VALUE VALUE)`

The special expression `set-symbol!` evaluates SYMBOL-VALUE for a
variable name. It then evaluates `VALUE` and assigns it to the
variable name given.

`set-symbol!` always returns `null`. 

`set-symbol!` is primarily intended for metaprogramming. You will
usually want to use [set!](Variables-Set.md).

The macro `set!` evaluates VALUE and assigns the result to SYMBOL in
the current scope.

`set-symbol!` raises an error if SYMBOL-VALUE does not evaluate to a
symbol.

Examples:

    > (set-symbol! (quote bananas) 5)
    null
    > bananas
    5
