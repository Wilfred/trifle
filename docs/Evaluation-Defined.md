# defined?

`(defined? SYMBOL)`

The function `defined?` returns `#true` if SYMBOL is defined in the
current context, and `#false` otherwise.

Examples:

```lisp
> (defined? (quote +))
#true
> (defined? (quote foo))
#false
> (set! foo 1)
null
> (defined? (quote foo))
#true
```
