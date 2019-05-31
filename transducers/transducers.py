from typing import Union, Iterable, Set

from transducers.typing import Coll, Fn
from transducers.protocols import protocol
import transducers.protocols as p


# TODO
# - mapcat
# - take-while (uses reduced)
# - drop-while
# - take-nth
# - interpose (uses reduced)
# - partition-all
# - halt-when (uses reduced)


def identity(x):
    return x


def complement(f):
    """
    Returns a function calls `f` and negates the result before returning it.
    """

    def f2(*args):
        return not f(*args)

    return f2


def comp(f, *fs):
    if len(fs) == 0:
        return f
    elif len(fs) == 1:
        g = fs[0]

        def composition(*args):
            return f(g(*args))

        return composition
    elif len(fs) == 2:
        g, h = fs

        def composition(*args):
            return f(g(h(*args)))

        return composition
    elif len(fs) == 3:
        g, h, i = fs

        def composition(*args):
            return f(g(h(i(*args))))

        return composition
    else:
        fs = [f] + list(fs)
        first = fs[-1]

        def composition(*args):
            return reduce(lambda x, f2: f2(x), first(*args), fs[:-1])

        return composition


# declare a new collection protocol
collection = protocol("conj", "conj_iterable", "empty")


def conj(coll, *xs) -> Coll:
    """
    Conjoin the value x onto coll.
    """
    if len(xs) == 1:
        return collection.conj(coll, xs[0])
    elif not xs:
        return coll
    return collection.conj_iterable(coll, xs)


def empty(coll) -> Coll:
    """
    Return a new empty coll of type `coll`.
    """
    return collection.empty(coll)


custom_iterator = protocol("iterator")


def iterator(coll: Iterable) -> Iterable:
    """
    Get (possibly custom) iterator for the coll.
    """
    try:
        return custom_iterator.iterator(coll)
    except:
        return iter(coll)


def map(f: Fn, *rest: Iterable):
    if rest:
        if len(rest) == 1:
            return (f(x) for x in iterator(rest[0]))
        else:
            return (f(*xs) for xs in zip(*(iterator(r) for r in rest)))
    else:

        def xform(rf):
            def rf2(*args):
                if len(args) == 1:
                    return rf(*args)
                elif len(args) == 2:
                    init, x = args
                    return rf(init, f(x))
                raise TypeError(
                    f"Some arities of transducing `map` not yet supported ({args})."
                )

            return rf2

        return xform


def filter(pred: Fn, *rest: Iterable):
    """
    Filter values from iterable such that only those where pred(x) is truthy.
    """
    if rest:
        if len(rest) == 1:
            return (x for x in iterator(rest[0]) if pred(x))
        raise TypeError("Can't `filter` on more than one collection.")
    else:

        def xform(rf):
            def rf2(*args):
                if len(args) == 1:
                    return rf(*args)
                elif len(args) == 2:
                    init, x = args
                    if pred(x):
                        return rf(init, x)
                    return init
                raise TypeError(
                    f"Some arities of transducing `filter` not yet supported ({args})."
                )

            return rf2

        return xform


def remove(pred: Fn, *rest: Iterable):
    """
    Like `filter` but removes values from iterable where pred(x) is truthy.
    """
    return filter(complement(pred), *rest)


class Reduced:
    def __init__(self, value):
        self.value = value


def ensure_reduced(value) -> Reduced:
    """
    Ensure the value is wrapped with a reduced wrapper.
    """
    if isinstance(value, Reduced):
        return value
    return Reduced(value)


def preserving_reduced(rf):
    """
    Wrap a reduced result with a second reduced wrapper; for nested
    reductions.
    """

    def rf2(init, x):
        init = rf(init, x)
        if isinstance(init, Reduced):
            return Reduced(init)
        return init

    return rf2


def __take_generator(n: int, coll: Iterable):
    """
    Helper function to implement `take` generator.
    """
    for i, x in enumerate(iterator(coll)):
        if i < n:
            yield x
        else:
            break


def take(n: int, *rest: Iterable):
    if rest:
        if len(rest) == 1:
            return __take_generator(n, rest[0])
        raise TypeError("Can't `take` on more than one collection.")
    else:

        def xform(rf):
            seen = n

            def rf2(*args):
                nonlocal seen
                if len(args) == 1:
                    return rf(*args)
                elif len(args) == 2:
                    init, x = args
                    if seen > 0:
                        seen -= 1
                        return rf(init, x)
                    return ensure_reduced(init)
                raise TypeError(
                    f"Some arities of transducing `take` not yet supported ({args})."
                )

            return rf2

        return xform


def __drop_generator(n: int, coll: Iterable):
    """
    Helper function to implement `drop` generator.
    """
    for i, x in enumerate(iterator(coll)):
        if i >= n:
            yield x


def drop(n: int, *rest: Iterable):
    if rest:
        if len(rest) == 1:
            return __drop_generator(n, rest[0])
        raise TypeError("Can't `drop` on more than one collection.")
    else:

        def xform(rf):
            seen = n

            def rf2(*args):
                nonlocal seen
                if len(args) == 1:
                    return rf(*args)
                elif len(args) == 2:
                    init, x = args
                    if seen <= 0:
                        return rf(init, x)
                    seen -= 1
                    return init
                raise TypeError(
                    f"Some arities of transducing `drop` not yet supported ({args})."
                )

            return rf2

        return xform


def __distinct_generator(coll: Iterable) -> Iterable:
    s: Set = set()
    for x in coll:
        if x not in s:
            s.add(x)
            yield x


def distinct(*rest: Iterable):
    if rest:
        if len(rest) == 1:
            return __distinct_generator(rest[0])
        raise TypeError("Can't `drop` on more than one collection.")
    else:

        def xform(rf):
            s = set()

            def rf2(*args):
                nonlocal s
                if len(args) == 1:
                    return rf(*args)
                elif len(args) == 2:
                    init, x = args
                    if x not in s:
                        s.add(x)
                        return rf(init, x)
                    return init
                raise TypeError(
                    f"Some arities of transducing `distinct` not yet supported ({args})."
                )

            return rf2

        return xform


def __dedupe_generator(coll: Iterable) -> Iterable:
    stub = object()
    last = stub
    for x in coll:
        if last is stub or x != last:
            last = x
            yield last


def dedupe(*rest: Iterable):
    if rest:
        if len(rest) == 1:
            return __dedupe_generator(rest[0])
        raise TypeError("Can't `drop` on more than one collection.")
    else:

        def xform(rf):
            stub = object()
            last = stub

            def rf2(*args):
                nonlocal last
                if len(args) == 1:
                    return rf(*args)
                elif len(args) == 2:
                    init, x = args
                    if last is stub or x != last:
                        last = x
                        return rf(init, x)
                    return init
                raise TypeError(
                    f"Some arities of transducing `distinct` not yet supported ({args})."
                )

            return rf2

        return xform


def reduce(f: Fn, init, coll: Iterable):
    """
    Reduce `coll` onto `init` using the reducing function `f`.
    Returns the result of the reduction when:
    - a reduction step yields a value marked as Reduced, or 
    - there are no more values in `coll` to reduce.
    """
    for x in iterator(coll):
        init = f(init, x)
        if isinstance(init, Reduced):
            init = init.value
            break
    return init


def __safe_completing(f):
    def f2(arg, *rest):
        if not rest:
            try:
                return f(arg)
            except TypeError:
                return arg
        return f(arg, *rest)

    return f2


def transduce(xform: Fn, f: Fn, init, coll: Iterable):
    """
    Reduces `coll` onto `init` using the result of applying the transducing
    function `xform` to the reducing function `f`. Returns the result of the
    reduction.
    """
    f = xform(__safe_completing(f))
    ret = reduce(f, init, coll)
    return f(ret)


def into(init, *rest):
    """
    Reduces a coll into the `init` collection. `init` must support `conj`.
    If a transducing function is provided, applies transducer while reducing
    into `init`.
    """
    if len(rest) == 1:
        return reduce(conj, init, rest[0])
    elif len(rest) == 2:
        xform, coll = rest
        return transduce(xform, conj, init, coll)
    else:
        raise TypeError("Can't `into` without a source or with more than one source.")


def generate(xform: Fn, coll: Iterable) -> Iterable:
    """
    Returns a generator which transduces the `coll` using `xform`,
    and yields the result.
    """
    f = xform(lambda x, y: y)
    stub = object()
    init = stub
    for x in iterator(coll):
        init = f(init, x)
        if isinstance(init, Reduced):
            if init.value is not stub:
                yield init.value
            return
        if init is not stub:
            yield init
            init = stub


def into_new(xform: Fn, coll: Coll) -> Coll:
    """
    Transduce `coll` into a new empty coll of the same type, while
    applying transducing funtion `xform` to the sequence.
    """
    return into(empty(coll), generate(xform, coll))


def __concat_generator(colls: Iterable[Iterable]):
    for coll in colls:
        yield from coll


def concat(*colls: Iterable):
    """
    Concatenate the values from 1 or more colls into a single sequence.
    If no colls are provided, returns a transducer.
    """
    if colls:
        return __concat_generator(colls)

    else:

        def xform(rf):
            rrf = preserving_reduced(rf)

            def rf2(*args):
                if len(args) == 1:
                    return rf(*args)
                elif len(args) == 2:
                    init, x = args
                    return reduce(rrf, init, x)
                raise TypeError(
                    f"Some arities of transducing `concat` not yet supported ({args})."
                )

            return rf2

        return xform


# extend collection protocol for built in list, set, dict, str
collection.extend(
    list,
    ("conj", lambda l, x: l.append(x) or l),
    ("conj_iterable", lambda l, iterable: l.extend(iterable) or l),
    ("empty", lambda _: []),
)

collection.extend(
    set,
    ("conj", lambda s, x: s.add(x) or s),
    ("conj_iterable", lambda s, iterable: s.update(iterable) or s),
    ("empty", lambda _: set()),
)

collection.extend(
    dict,
    ("conj", lambda d, t: d.update([t]) or d),
    ("conj_iterable", lambda d, iterable: d.update(iterable) or d),
    ("empty", lambda _: {}),
)

collection.extend(
    str,
    ("conj", lambda s, x: s + x),
    ("conj_iterable", lambda s, iterable: "".join(x for x in concat([s], iterable))),
    ("empty", lambda _: ""),
)

# use dict.items as the iterator accessor for built in dict
# (lets us transduce from one dict into another dict)
custom_iterator.extend(dict, ("iterator", lambda d: d.items()))
