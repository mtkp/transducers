mtkp/transducers
================

Experimental transducers (a la Clojure) for Python. Includes general
functional abstractions such as `map`, `filter`, `reduce`, in addition
to `transduce`. Also includes a simple protocol (interface) implementation
for Python which allows dynamic extensions on top of arbitrary python types
(including builtins).

# Usage

```py3
import transducers as t

# use transducers to transform a collection
l1 = [1, 2, 3, 2, 1, 2, 3]
l2 = []
t.into(l2, t.distinct(), l1)
print(f"{l2}")

# alternatively, `into_new`
l3 = t.into_new(t.distinct(), l1)
print(f"{l3}")

# chain together transducers with comp:
source = range(1, 1000000000)
squares_divisible_by_three = t.comp(
    t.map(lambda x: x ** 2),
    t.filter(lambda x: x % 3 == 0),
    t.take(5),
)

# get the first 5 squares of the source where the square is
# divisible by 3. will not realize the source beyond what is
# needed by the transducer.
for x in t.generate(squares_divisible_by_three, source):
    print(f"{x}")

# recreate an example from https://www.clojure.org/reference/transducers
# (def xf (comp (filter odd?) (map inc)))
# (transduce xf + (range 5))
# ;; => 6
# (transduce xf + 100 (range 5))
# ;; => 106

xf = t.comp(
    t.filter(lambda x: x % 2 == 1),
    t.map(lambda x: x + 1)
)
t.transduce(xf, lambda x, y: x + y,   0, range(5))
# => 6
t.transduce(xf, lambda x, y: x + y, 100, range(5))
# => 106


```

## Dev

Requires `mypy` and `black`.

```sh
# run mypy (make check) and the transducer tests
make test

# run python black formatter
make format
```
