# join!

`(join! SEQUENCE :rest SEQUENCES)`

The function `join!` modifies SEQUENCE by appending every value from
every sequence in SEQUENCES. It returns `#null`.

```lisp
> (set! x (list 1 2))
#null
> (join! x (list 3 4) (list 5))
#null
> x
(1 2 3 4 5)
```
