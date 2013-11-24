# Trifle Lisp
#### *A sweet and friendly lisp*

Current status: Very very litle implemented.

Trifle is:

### Modular

Trifle actively avoids including a standard library. Instead, it opts
for including a package manager so that each package can evolve
separately. Packages use [semantic versioning](http://semver.org/) and
declare their dependencies.

### Iterating

The Trifle standard is not set in stone. Major versions may break
backwards compatibility. The featureset will change over time to
maximise readability and expressiveness.

### Self-documenting

Trifle seeks to make code understandable, when looking at both
individual pieces of code or the high-level overview. Trifle supports
docstrings and cross-references to package documentation.

Names are chosen to be clear, self-explanatory and minimally
abbreviated. Code should be concise through well-chosen abstraction
instead of very short names.

### Expressive

Trifle features closures, unhygenic macros and reader macros.

### Re-Examined

Trifle re-considers traditional lisp features. There is no built-in
Cons cell (lists are vectors). Some common functions have been renamed
(car) and others have different behaviours to other lisps (last
returns the last element in a list). Trailing parentheses are
encouraged to aid readability.

### Friendly

The Trifle community strives to be friendly and helpful. We have a
code of conduct that applies to all official Trifle communication
channels.

The language and its libraries are developed in the open on
GitHub. The package manager allows different forks of libraries to
coexist.

### Fast Enough

The Trifle interpreter is implemented in RPython so gets a JIT for
free. The language provides also provides basic TCO.

## Licensing

All code in this repository is LGPLv3. All documentation (including
feature proposals is CC-BY. The only exception is the code of conduct,
which is
[under a separate license](https://twitter.com/brian_curtin/status/389752035169423361).

## Missing Features

A new programming language should really have a good answer to 'how do
I run it in the browser?', 'how do I scale it to multiple cores?' and
'how do I interface with C code?'. Since this is an experimental
language, we are cheerfully ignoring these questions for now.
