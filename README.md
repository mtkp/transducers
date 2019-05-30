mtkp/transducers
================

Experimental transducers (a la Clojure) for Python. Also incldues
a simple protocol (interface) implementation for Python which allows dynamic
extension to arbitrary python types.

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
```
