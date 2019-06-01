from typing import Dict, Iterable

from transducers.typing import Coll, Fn
import transducers.transducers as t


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


__invert_dict = t.map(lambda tup: (tup[1], tup[0]))


def invert_dict(d: Dict) -> Coll:
    return t.into_new(__invert_dict, d)


def map_kvs(kfn: Fn, vfn: Fn, d: Dict):
    xf = t.map(lambda tup: (kfn(tup[0]), vfn(tup[1])))
    return t.into_new(xf, d)


def map_keys(f: Fn, d: Dict):
    return map_kvs(f, t.identity, d)


def map_vals(f: Fn, d: Dict):
    return map_kvs(t.identity, f, d)


def group_by(f: Fn, coll: Iterable):
    """
    Group the values of `coll` in a dict using the key function `f` on each
    value to determine the group. Returns a dict keyed by the results of `f`
    on the values of `coll`.
    """

    def rf(acc, v):
        k = f(v)
        if k in acc:
            acc[k].append(v)
        else:
            acc[k] = [v]
        return acc

    return t.reduce(rf, {}, coll)


def index(f: Fn, coll: Iterable):
    """
    Like `group_by` but only indexes one value per key. If multiple values
    map to the same key, indexes the latest value.
    """

    def rf(acc, v):
        acc[f(v)] = v
        return acc

    return t.reduce(rf, {}, coll)
