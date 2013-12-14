# Trifle Lisp
#### *A sweet and friendly lisp*

Current status: Only a very basic interpreter implemented. Please see
[the docs](docs/Introduction.md) to see what's available.

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

That said, the Trifle community will promote a set of defaults, so new
users have a standard set of tools to get started with.

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

Influences: Python's readability

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

## Missing Features

A new programming language should really have a good answer to 'how do
I run it in the browser?', 'how do I scale it to multiple cores?' and
'how do I interface with C code?'. Since this is an experimental
language, we are cheerfully ignoring these questions for now.
