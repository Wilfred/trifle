# Conventions

Trifle lisp has a conventions to keep code and documentation
consistent.

## Code

### Naming
Variable names use hyphens, e.g. `find-dessert`. Functions that return
booleans end with a question mark, e.g. `is-tasty?`. Functions that
modify state end with an exclamation mark, e.g. `eat-dessert!`.

### Formatting
Trifle code uses trailing parentheses to make scopes more obvious. If
the open parenthesis is on a different line, the closing parenthesis
should be on its own line. For example:

```lisp
(do
  (set! x 1)
)
```

## Documentation

Trifle lisp is documented using GitHub flavoured markdown. Every
built-in expression should be documented with a separate page. This
should include a summary of what it does, what arguments it takes, and
any errors it may throw. It should also include examples wherever
possible.
