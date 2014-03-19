## Initial Feature Set

### core

`lambda`

`set-symbol!` `set!` (CL: `setq`)

`eval` `apply` `parse` (CL: `read`)

`func` `func?`

`if` (using Python-style truthiness) `do` `let` (CL: `let*` but
without pairing up each binding, similar to Clojure) `while`

`load-file` `load-from-file`

### List

A dynamic array, not a linked list.

list? list first rest

second third fourth fifth

map for-each length empty? equal? append append! push! pop!

get-index set-index!

List literals are mutable, so the following is valid:

    (let (x '(1 2 3))
       (push! x 4))

### Boolean

bool? truthy? when unless not or and

### Null

null?

### Math

+ - * / mod exp abs div floor ceil round > < <= >= == sin cos tan odd? even?

number? float? integer?

E PI

### String

Strings are effectively lists of unicode characters. Character are a
distinct type.

uppercase lowercase

ALPHABET ALPHANUMERIC

substring length append string? equal? ->bytes (Python: `.encode`)
format

### Sequence

Generic functions that handle lists, strings and sets.

all? any? sequence?

first second third fourth fifth

flatten reduce equal? length set-at! value-at empty? subseq reverse
reverse! copy deepcopy append append!

zip filter map for-each

freeze unfreeze frozen?

### Hash-map

hash-map hash-map?

keys values items

set-item! has-key? equal? empty? merge merge!

### Hash-set

O(1) insert and search, unordered container.

hash-set hash-set?

add-value! has-value? length empty? union intersect

### IO

open-handle! close-handle! file-handle? is-open? read! read-all! seek!
peek write! position

STDIN STDOUT

print

### Byte sequence

Mutable vector of bytes.

`->string` (Python: `.decode`) byte-at set-byte! push! pop! length
byte-seq byte-seq? equal?

### Filesystem

join-path split-path SOURCE-PATH (Python: `__FILE__`) exists? file?
directory? readable? writable? directory-contents parent-directory

### Functions

function? set-function!

`set-function!` is important -- if function objects are mutable, it's
possible to implement Emacs-style advice even if there are multiple
references to a function (cf. the difficulty with monkey-patching in
Python which depends on how things were imported).

### Syntax and Syntactic Sugar

`no-eval` (lisp: `backquote`)
`eval` (lisp: `unquote`)
`eval*` (lisp: `unquote-splicing`)

`"foo"` string (can contain newlines)
`{a 1 b 2}` hash-map
make-unique-symbol (Clojure feature)

`#set(1 2)` hash-set reader syntax
`#bytes(254 254 255)` byte sequence reader syntax

`:foo` keyword symbol (evaluates to itself)

Docstring conventions:

"Takes argument FOO and calls [bar] on it.

>> (quux 1)
2"

### Reader macros

Reader macros should start with `#` and end with
balanced parentheses. E.g. `#foo(quux :baz)`.

Question: should we use this syntax for true/false/null?

### Exceptions

Catching exceptions:

```lisp
(try
 (call-dodgy-func)
 :catch (:zero-division)
 :catch (:type-error (call-restart :try-again))
 :finally (cleanup)
)
```

Throwing exceptions:

```lisp
(throw {:kind :value-error :message "Woah, I didn't expect that!"})
```

Offering restarts (which are dynamically scoped):

```lisp
(try
  (call-dodgy-func)
  :restart (:return-null (lambda () #null))
  :restart (:retry (lambda () (call-dodgy-func)))
  :restart (:override-with (lambda (value) (foo value)))
)
```

## Unspecified

Sockets and other network functionality. About (Python: `sys.version`)

## Future

`set-as` (CL: `setf`), `let-as` (elisp: `destructuring-bind`)

Explore freezing and unfreezing for list, vector, string

## Reflection

Be reflective wherever possible, it makes the language more
expressive.

CL's condition system allows you to inspect 'exception handlers' at
runtime. JavaScript allows you to inspect the current stack, making
building a debugger straightforward.

## Classes

Implement as a library.

Favour upfront declaration of slots to aid static analysis.

Multiple dispatch, multiple inheritance, reuse Python's MRO algorithm.

## User testing

This is an interesting area that would be worthwhile to pursue.

Relevant papers:

* http://ecs.victoria.ac.nz/foswiki/pub/Events/PLATEAU/Program/plateau2011-stefik.pdf
* An Empirical Investigation into Programming Language Syntax
