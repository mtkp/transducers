from typing import Dict, Iterable

from transducers.typing import Coll
import transducers.transducers as t


def invert_dict(d: Dict) -> Coll:
    invert = t.map(lambda tup: (tup[1], tup[0]))
    return t.into_new(invert, d)


def add(x, *xs):
    if not xs:
        return x
    elif len(xs) == 1:
        return x + xs[0]
    raise TypeError(f"Too many positional arguments to 'add' ({1 + len(xs)})")


def sum(coll: Iterable):
    return t.reduce(add, 0, coll)


def mult(x, *xs):
    if not xs:
        return x
    elif len(xs) == 1:
        return x * xs[0]
    raise TypeError(f"Too many positional arguments to 'mult' ({1 + len(xs)})")


def product(coll: Iterable):
    return t.reduce(mult, 1, coll)
