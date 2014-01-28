# parse

`(parse STRING)`

The function `parse` takes a string of Trifle code, and returns its
parsed representation as a list. `parse` can raise an error if STRING
is not syntactically valid.

Note that STRING may contain multiple top-level Trifle expressions, so
`parse` always returns a list.

Example:

    > (parse "1 2")
    (1 2)
    > (parse "(+ :foo bar)")
    ((+ :foo bar))
