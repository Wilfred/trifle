**Table of Contents** *generated with [autotoc](https://github.com/Wilfred/autotoc)*

- [Trifle Lisp](#trifle-lisp)
  - [Goals](#goals)
    - [Modular](#modular)
    - [Iterating](#iterating)
    - [Self-documenting](#self-documenting)
    - [Documented](#documented)
    - [Expressive](#expressive)
    - [Re-Examined](#re-examined)
    - [Accessible](#accessible)
    - [Friendly](#friendly)
    - [Fast Enough](#fast-enough)
    - [Missing Features](#missing-features)
  - [Release History](#release-history)
    - [v0.7](#v07)
    - [v0.6](#v06)
    - [v0.5](#v05)
    - [v0.4](#v04)
    - [v0.3](#v03)
    - [v0.2](#v02)
    - [v0.1](#v01)

# Trifle Lisp
#### *A sweet and friendly lisp*

Current status: Only a very basic interpreter implemented. Please see
[the docs](docs/Introduction.md) to see what's available.

[![Build Status](https://travis-ci.org/Wilfred/trifle.png?branch=master)](https://travis-ci.org/Wilfred/trifle)
[![Coverage Status](https://coveralls.io/repos/Wilfred/trifle/badge.png)](https://coveralls.io/r/Wilfred/trifle)

## Goals

Trifle is:

### Modular

Trifle actively avoids including a standard library. Instead, it opts
for including a package manager so that each package can evolve
separately. Packages use [semantic versioning](http://semver.org/) and
declare their dependencies.

Trifle takes an 'open implementation' approach. Wherever possible,
functionality is built on top of the core, to encourage
experimentation and to minimise the amount of non-Trifle code users
must read. Where non-essential functions are written in RPython for
performance, an equivalent Trifle implementation will be included.

In spite of encouraging libraries to live outside of the core, the
Trifle community will promote a set of defaults, so new users have a
standard set of tools to get started with.

Influences: Scheme's small core, CLOS as a library, npm, Smalltalk

### Iterating

The Trifle standard is not set in stone. Major versions may break
backwards compatibility. The featureset will change over time to
maximise readability and expressiveness.

Influences: Python 3 cleaning up semantics

### Self-documenting

Trifle seeks to make code understandable, when looking at both
individual pieces of code or the high-level overview. Trifle supports
docstrings and cross-references to package documentation.

Names are chosen to be clear, self-explanatory and minimally
abbreviated. Code should be concise through well-chosen abstraction
instead of very short names.

Influences: Python's readability, Python doctests, Elisp docstrings

### Documented

Trifle seeks to be clearly and thoroughly documented. Documentation
should include examples wherever possible. Each page in the
documentation should have a small and well-defined purpose, with each
function on a separate page. Users should be able to leave comments on
the documentation for later readers.

Influences: PHP docs, clojuredocs

### Expressive

Trifle features closures, unhygenic macros and reader macros.

Influences: Common Lisp

### Re-Examined

Trifle re-considers traditional lisp features. There is no built-in
Cons cell (lists are vectors). Some common functions have been renamed
(car) and others have different behaviours to other lisps (last
returns the last element in a list). Trailing parentheses are
encouraged to aid readability.

Influences: Clojure

### Accessible

Trifle places a high value on code readability for users who have
programmed in other languages but are new to Trifle (or lisps in
general). It tries to use familiar terminology and avoids
abbreviations.

### Friendly

The Trifle community strives to be friendly and helpful. We have a
code of conduct that applies to all official Trifle communication
channels.

The language and its libraries are developed in the open on
GitHub. The package manager allows different forks of libraries to
coexist.

Influences: Rust/CoffeeScript on GitHub

### Fast Enough

The Trifle interpreter is implemented in RPython so gets a JIT for
free. The language provides also provides basic TCO.

Influences: Pypy, Scheme

### Missing Features

A new programming language should really have a good answer to 'how do
I run it in the browser?', 'how do I scale it to multiple cores?' and
'how do I interface with C code?'. Since this is an experimental
language, we are cheerfully ignoring these questions for now.

## Release History

### v0.7

Bytestrings: Added the function `bytestring?`.

Sequences: Added the functions `empty`, `empty?`, `copy`, `join!` and
`join`.

Booleans: Removed `truthy?`. `if` and `while` now require booleans for
their conditions, instead of just truthy values.

Docs: Added a 'generic functions' section.

Generic functions: Added `identity`.

Numbers: Added a fraction type. Added support for fractions to `+`,
`-`, `*` and `/`.

Errors: Various minor improvements to error messages to be more
consistent and helpful.

### v0.6

Installation: It's now possible to do `make install` and `make
uninstall` to install a Trifle interpreter.

Prelude: The interpreter is now more helpful when it can't find the
prelude (instead of crashing).

Escape sequences: Trifle now supports backslash escape sequences in
strings and characters, so `'\''` and `"they said \"hello\""` are now
legal literals.

Booleans: Added short-circuiting macros `and` and `or`.

Numbers: Added the functions `>`, `>=` and `<=`.

Equality: Fixed a bug where character equality considered characters
to not be `equal?` if they are not `same?`. Identical characters are
now equal, so `(equal? 'a' a')` is `#true`.

Lists: Added the built-in function `insert!`. `append!` and `push!` have been
rewritten as Trifle functions in the prelude. Added the function `filter`.

Special expressions: Special expressions are no longer first class
values. You can no longer do things like `(set! foo if)` or
`((lambda (f x y) (f x y)) if #true 1)`. This is intended to make
static analysis more tractable.

### v0.5

Strings: Strings are now sequences of characters and all sequence
functions (`get-index`, `set-index!`, `append!`, `push!`, `length`,
`map`, `rest`, `first`, `second`, `third`, `fourth`, `fifth`, and
`last`) can be called on them. Also added a `string?` function.

Character: Added a character datatype. Added a `character?` function.

Errors: Fixed error messages in `length` and `parse` which incorrectly
stated the expected type.

Docs: Fixed some minor mistakes.

### v0.4

Bytestrings: 'Bytes' are now called bytestrings, and literal
bytestrings are recognised by the interpreter
(e.g. `#bytes("abc")`). Bytestrings are now mutable.

Sequences: Trifle now has the concept of a 'sequence', which is a
mutable ordered datatype. Lists and bytestrings are both
sequences. The expressions `length`, `get-index`, `set-index!`,
`first`, `second`, `third`, `fourth`, `fifth`, `append!` and `map` now
handle sequences. Added the function `last`. The macro `for-each` now
handles sequences.

Lists: Added the functions `list?`, `rest` and `range`.

Booleans: The literal boolean syntax has changed to `#true` and
`#false`. Added the macros `unless` and `case`. `truthy?` has moved to
the prelude. The values `""`, `#bytes("")` and `0.0` are now considered
to be falsey.

Null: The literal null syntax has changed to `#null`.

Strings: `print` is now `print!`.

Numbers: Added the functions `zero?`, `mod` and `div`.

Errors: `get-index`, `set-index!` and `push!` now use arity errors and value
errors where appropriate. Fixed some error wording issues with `open`.

IO: Added an `exit!` function.

Evaluation: `quote` is now much stricter about arguments passed to
`unquote` and `unquote*` instead of silently ignoring them. `call` can
now handle macros as well as functions.

Interpreter: When given the path to a function, the result of the
program is no longer automatically printed. Use `print!` in your
program instead.

Editing: There is now an Emacs major mode available, see
[Getting Started](docs/Getting-Started.md).

Sample programs: Added [hello world](sample_programs/hello_world.tfl),
[fibonacci](sample_programs/fibonacci.tfl) and
[fizzbuzz](sample_programs/fizzbuzz.tfl) sample programs.

Licensing: Trifle is now dual-licensed under MIT and Apache 2.0. This
will not change again.

### v0.3

File handles: Added a file handle datatype, and added the functions
`open`, `close`, `read` and `write!`.

Bytes: Added a bytes datatype, and added the function `decode`.

Strings: Fixed many unicode bugs. Added the function `encode`.

Equality: Added the function `equal?`. `same?` no longer treats
numbers specially, so it's now possible for two numbers to be `equal?`
but not `same?`. `same?` now throws ArityError if given the wrong
number of arguments.

Built-in functions: String representations have been improved.

Docs: The documentation has been grouped into more logical sections,
and datatypes have been separated from other documentation pages.

### v0.2

Numbers: This release adds floats, and makes parsing stricter. `123foo`
was previously a symbol, it is now a syntax error. The function `/`
and macro `dec!` have been added.

Evaluation: The functions `call`, `parse`, `eval` and `defined?` have
been added.

Macros: Fixed a bug with `macro` where it reported the
wrong argument as incorrect. Macros now always require a body.

Errors: Many built-in functions have had their error messages
improved, and raise an arity error (not a type error) on the wrong
number of arguments.

Documentation: Docs have been improved, and `function` and `let` have
gained docmentation. We've cleared up the difference between functions
(arguments always evaluated) and special expressions (does not
evaluate some arguments).

I/O: The function `input` (read a line from stdin) has been added.

Workflow: We now use coveralls to measure code coverage on Python code
for every checkin. Note we don't have any facility for measuring
coverage on Trifle code yet.

### v0.1

This release includes integers, lists, booleans, strings (though you
can do little with strings currently), symbols, loops, functions,
closures and macros.
