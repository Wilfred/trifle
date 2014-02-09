These are medium to long term goals, since the language needs to be
relatively stable before we can build a sophisticated toolset.

## REPL

Trifle aboslutely needs a basic REPL. This should be just another
package, so it can evolve separately or be replaced by other
implementations as the user wishes.

### Extension: Emacs Integration

This would be a great help. Getting basic inferior-lisp functionality
would be straightforward, but ideally there would be docstrings in the
minibuffer, macroexpansion, jumping to relevant functions, and jumping
to manual crossreferences.

### Extension: Persistence

Ideally the REPL would persist its state to disk when the session is
closed, so starting the REPL again later would let the dev continue
where he/she left off.

Functions should know which line they were defined on.

## Packaging

The user should be able to package up groups of files that can be
installed elsewhere.

### Extension: Versioning

Trifle packages should support semver dependencies, allowing and
encouraging users to specify what their project depends on. It should
make it easy to say 'I depend on foo 1.2+, but less that 2.0'.

### Extension: -auto-import.tfl

Assume I have a package `foo` that contains `foo/bar:some-function`. I
want to be able to define `foo/-auto-import.tfl` that imports
`foo/bar`, so users of the package can access `foo:some-function`.

### Extension: Sandboxing

This needs to be available to all users, building on the dependency
versioning.

### Extension: Introspectable Packages

Ideally programs would be able to see which packages have been loaded,
and which package each function belongs to. A package should become a
top-level type.

### Extension: Central Server

We need a central server that users can upload their packages to. Note
that the download tool should cache packages, so multiple projects
using the same package only requires downloading once.

## Editor

Trifle would benefit from a built-in editor. This should be strongly
Emacs influenced, and similarly start with a conservative default
configuration (e.g. C-c, C-x, C-v clipboard, paredit disabled).

This is partly to give users something to work with out-of-the-box,
(cf. Dr Racket or IDLE) and to encourage the core devs to collaborate
on a common editing environment (cf. Smalltalk).

## Debugger

A basic debugger would be a huge help.

### Extension: Time Travel

Not enough languages have this, and it's a great help in many circumstances.
