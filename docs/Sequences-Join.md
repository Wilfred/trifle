# join

`(join SEQUENCE :rest SEQUENCES)`

The function `join` returns a copy of SEQUENCE with every value from
every sequence in SEQUENCES appended.

```lisp
> (join (list 1 2) (list 3) (list) (list 4))
(1 2 3 4)
```
