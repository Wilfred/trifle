# Variables

Trifle lisp supports variables. When you assign to undefined variable,
it is defined in the innermost scope. Otherwise, you change the
variable in the innermost scope where it is defined.

Examples:

Defining a variable in global scope:

```lisp
> (set! x 1)
null
> x
1
```

Defining a variable in a function's scope:

```lisp
> ((lambda () (set! x 1) x))
1
```

If a variable is already defined in a outer scope, it will be updated:

```lisp
> (set! x 1)
null
> ((lambda () (set! x 2)))
null
> x
2
```

## Variable special expressions

1. [set-symbol!](Variables-SetSymbol.md)

## Variable macros
1. [set!](Variables-Set.md)
