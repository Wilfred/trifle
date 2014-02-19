# truthy?

`(truthy? VALUE)`

The function `truthy?` converts its argument to a boolean. The values
`0`, `()` and `false` are considered 'falsey', all other values return
`true`.

Examples:

    > (truthy? 0)
    #false

    > (truthy? 1)
    #true

    > (truthy? (quote ()))
    #false
