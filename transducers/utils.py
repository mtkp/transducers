from typing import Dict, Iterable

from transducers.typing import Coll
import transducers.transducers as t


def invert_dict(d: Dict) -> Coll:
    invert = t.map(lambda tup: (tup[1], tup[0]))
    return t.into_new(invert, d)


def sum(coll: Iterable):
    return t.reduce(lambda x, y: x + y, 0, coll)
