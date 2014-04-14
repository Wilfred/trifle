# Strings

Trifle supports strings. Strings are mutable sequences of
[characters](Characters.md).

String literals consist of unicode characters between double quotes,
e.g. `"blancmange"` and `"flambé"`. Any character may occur between
double quotes (including newlines), except backslashes and single
quotes. The following escaped characters are recognised: `"\\"`,
`"\""`, `"\n"`.

## String functions

Predicates:

1. [string?](Strings-StringPredicate.md)
2. [empty?](Sequences-EmptyPredicate.md)

Creating a new string:

1. [input](Strings-Input.md)
2. [rest](Sequences-Rest.md)
3. [map](Sequences-Map.md)
4. [filter](Sequences-Filter.md)
5. [empty](Sequences-Empty.md)
6. [copy](Sequences-Copy.md)

Accessing:

1. [get-index](Sequences-GetIndex.md)
2. [length](Sequences-Length.md)
3. [first](Sequence-First.md)
4. [second](Sequences-Second.md)
5. [third](Sequences-Third.md)
6. [fourth](Sequences-Fourth.md)
7. [fifth](Sequences-Fifth.md)
8. [last](Sequences-Last.md)

Modifying:

1. [set-index!](Sequences-SetIndex.md)
2. [insert!](Sequences-Insert.md)
3. [append!](Sequences-Append.md)
4. [push!](Sequences-Push.md)

Converting to other types:

1. [encode](Strings-Encode.md)
