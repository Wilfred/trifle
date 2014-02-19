# quote

`(quote EXPRESSION)`

The special expression `quote` takes a single argument, and returns it
unevaluated.

Examples:

```lisp
> (quote (+ 1 2)
(+ 1 2)

> (quote 1)
1
```

If `quote` is given a list that contains lists of the form `(unquote EXPRESSION)`, those
expressions will be evaluated.

Examples:

```lisp
> (set! x 1)
#null
> (quote (x (unquote x))
(x 1)
```

If `quote` is given a list that contains lists of the form
`(unquote EXPRESSION...)`, those expressions will be evaluated and
included in the parent list.

Examples

```lisp
> (set! x 1)
#null
> (quote (x (unquote* (list x x))))
(x 1 1)
> (quote (x (unquote (list x x))))
(x (1 1))
```
