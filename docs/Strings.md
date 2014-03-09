# Strings

Trifle supports strings. Strings are mutable sequences of unicode code
points.

String literals consist of characters between double quotes,
e.g. `"blancmange"` and `"flambé"`. Backslashes are not permitted
between double quotes. Any other character may occur, including
newlines.

## String functions

Predicates:

1. [string?](Strings-StringPredicate.md)

Creating a new string:

1. [input](Strings-Input.md)
2. [map](Sequences-Map.md)
3. [rest](Sequences-Rest.md)

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
2. [append!](Sequences-Append.md)
3. [push!](Sequences-Push.md)

Other:

1. [print!](Strings-Print.md)
2. [encode](Strings-Encode.md)
