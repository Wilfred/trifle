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

list? list first (CL: `car`) rest (CL: `cdr`) set-first! set-rest!

second third fourth fifth

map for-each length empty? append append! push!

All lists are proper.

### Boolean

bool? truth? when unless not or and

### Math

+ - * / mod exp abs div floor ceil round > < <= >= == sin cos tan odd? even?

number? float? integer?

E PI

### String

Strings are effectively immutable vectors of unicode characters.

uppercase lowercase

ALPHABET ALPHANUMERIC

substring length append string? equal? ->bytes (Python: `.encode`)
format

### Vector

A dynamic array supporting heterogeneous types.

vector? vector set-at! value-at length push! pop append append! equal?

### Sequence

Generic functions that handle lists, vectors, strings or hash-sets.

all? any? sequence?

first second third fourth fifth

flatten reduce equal? length set-at! value-at empty? subseq reverse
reverse! copy deepcopy append append!

zip filter map for-each

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

### Syntactic Sugar

`'` quote
backquote
`,` unquote
`,@` unquote-splicing (TODO: can we do better?)
`"foo"` string (can contain newlines)
`[1 2]` vector
`{a 1 b 2}` hash-map
`~` make-unique-symbol (Clojure feature)

`#set(1 2)` hash-set reader syntax
`#bytes(254 254 255)` byte sequence reader syntax

`:foo` keyword symbol (evaluates to itself)

Docstring conventions:

"Takes argument FOO and calls <bar> on it.

>> (quux 1)
2"

## Unspecified

Sockets and other network functionality. About (Python: `sys.version`)

## Future

`set-as` (CL: `setf`), `let-as` (elisp: `destructuring-bind`)

Explore freezing and unfreezing for list, vector, string
