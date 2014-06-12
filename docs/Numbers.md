# Numbers

Trifle supports integers, fractions and floats.

Integer literals are made from digits. Example integers are `0`,
`1234` and `-999999`. You may also use underscores to group digits,
e.g. `1_000_000`.

Underscores may occur anywhere in numbers, except at the start. `_1`
is treated as a symbol, not a number.

Fractions literals are digits with a forward slash. Example fractions
are `1/2`, `6/5` and `1/1_000`.

Float literals are made from digits and a single decimal
point. Example floats are `1.1` and `0.123`. As with integers, you can
use underscores in float literals: `1_000.000_001`.

Integers and frations are arbitrary size in Trifle, and never overflow.

## Number functions

1. [+](Numbers-Add.md)
2. [-](Numbers-Subtract.md)
3. [*](Numbers-Multiply.md)
3. [/](Numbers-Divide.md)
4. [mod](Numbers-Mod.md)
5. [div](Numbers-Div.md)
6. [>](Numbers-LessThan.md)
7. [>=](Numbers-LessThanEqual.md)
8. [<](Numbers-GreaterThan.md)
9. [<=](Numbers-GreaterThanEqual.md)
10. [inc](Numbers-Inc.md)
11. [dec](Numbers-Dec.md)
12. [zero?](Numbers-ZeroPredicate.md)

## Number macros

1. [inc!](Numbers-IncMacro.md)
2. [dec!](Numbers-DecMacro.md)
