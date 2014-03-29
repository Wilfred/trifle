# Lists

Trifle supports lists. A list is a mutable collection of values that may be
accessed by index.

Lists in Trifle are implemented as dynamic arrays, with O(1) access
and updating.

## List functions

Predicates:

1. [list?](Lists-ListPredicate.md)

Creating a new list:

1. [list](Lists-List.md)
2. [rest](Sequences-Rest.md)
3. [map](Sequences-Map.md)
4. [filter](Sequences-Filter.md)
5. [range](Lists-Range.md)

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
