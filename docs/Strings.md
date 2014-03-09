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

Modifying:

1. [set-index!](Sequences-SetIndex.md)

Other:

1. [print!](Strings-Print.md)
2. [encode](Strings-Encode.md)
