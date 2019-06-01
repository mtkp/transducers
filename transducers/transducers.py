from typing import Union, Iterable, Set, List

from transducers.typing import Coll, Fn
from transducers.protocols import protocol
import transducers.protocols as p


# TODO
# - take-while (uses reduced)
# - drop-while
# - take-nth
# - interpose (uses reduced)
# - halt-when (uses reduced)
# - keep-indexed


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
collection = protocol("conj_one", "conj_iterable", "is_immutable", "empty")


def conj(coll: Coll, *xs) -> Coll:
    """
    Conjoin the value x onto coll.
    """
    if len(xs) == 1:
        return collection.conj_one(coll, xs[0])
    elif not xs:
        return coll
    return collection.conj_iterable(coll, xs)


def is_immutable(coll: Coll) -> bool:
    try:
        return collection.is_immutable(coll)
    except:
        return False


def empty(coll: Coll) -> Coll:
    """
    Return a new empty coll of type `coll`.
    """
    return collection.empty(coll)


custom_iter = protocol("iter")


def iterator(coll: Iterable) -> Iterable:
    """
    Get (possibly custom) iterator for the `coll`.
    """
    try:
        return custom_iter.iter(coll)
    except:
        return iter(coll)


def map(f: Fn, *rest: Iterable):
    """
    Map values of iterable with `f`.
    """
    if rest:
        if len(rest) == 1:
            return (f(x) for x in iterator(rest[0]))
        else:
            return (f(*xs) for xs in zip(*(iterator(r) for r in rest)))

    def xform(rf):
        def rf2(init, *xs):
            if not xs:
                return rf(init)
            elif len(xs) == 1:
                return rf(init, f(xs[0]))
            raise TypeError(
                f"Some arities of transducing `map` not supported ({1 + len(xs)})."
            )

        return rf2

    return xform


def map_indexed(f: Fn, *rest: Iterable):
    """
    Map values with their indices of iterable. `f` should accept two arguments,
    an index and a value.
    """
    if rest:
        if len(rest) == 1:
            return (f(i, x) for i, x in enumerate(iterator(rest[0])))
        raise TypeError("Can't `map_indexed` on more than one collection.")

    def xform(rf):
        i = 0

        def rf2(init, *xs):
            nonlocal i
            if not xs:
                return rf(init)
            elif len(xs) == 1:
                res = rf(init, f(i, xs[0]))
                i += 1
                return res
            raise TypeError(
                f"Some arities of transducing `map_indexed` not supported ({1 + len(xs)})."
            )

        return rf2

    return xform


def filter(pred: Fn, *rest: Iterable):
    """
    Filter values from iterable such that only those where `pred` is truthy.
    """
    if rest:
        if len(rest) == 1:
            return (x for x in iterator(rest[0]) if pred(x))
        raise TypeError("Can't `filter` on more than one collection.")

    def xform(rf):
        def rf2(init, *xs):
            if not xs:
                return rf(init)
            elif len(xs) == 1:
                x = xs[0]
                if pred(x):
                    return rf(init, x)
                return init
            raise TypeError(
                f"Some arities of transducing `filter` not supported ({1 + len(xs)})."
            )

        return rf2

    return xform


def __keep_generator(f: Fn, coll: Iterable) -> Iterable:
    for x in iterator(coll):
        res = f(x)
        if res is not None:
            yield res


def remove(pred: Fn, *rest: Iterable):
    """
    Like `filter` but removes values from iterable where pred(x) is truthy.
    """
    return filter(complement(pred), *rest)


def keep(f: Fn, *rest: Iterable):
    """
    Map values from iterable, discarding any where f(x) is None.
    """
    if rest:
        if len(rest) == 1:
            return __keep_generator(f, rest[0])
        raise TypeError("Can't `keep` on more than one collection.")

    def xform(rf):
        def rf2(init, *xs):
            if not xs:
                return rf(init)
            elif len(xs) == 1:
                res = f(xs[0])
                if res is not None:
                    return rf(init, res)
                return init
            raise TypeError(
                f"Some arities of transducing `keep` not supported ({1 + len(xs)})."
            )

        return rf2

    return xform


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


def __take_generator(n: int, coll: Iterable) -> Iterable:
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

    def xform(rf):
        seen = n

        def rf2(init, *xs):
            nonlocal seen
            if not xs:
                return rf(init)
            elif len(xs) == 1:
                if seen > 0:
                    seen -= 1
                    return rf(init, xs[0])
                return ensure_reduced(init)
            raise TypeError(
                f"Some arities of transducing `take` not supported ({1 + len(xs)})."
            )

        return rf2

    return xform


def __drop_generator(n: int, coll: Iterable) -> Iterable:
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

    def xform(rf):
        seen = n

        def rf2(init, *xs):
            nonlocal seen
            if not xs:
                return rf(init)
            elif len(xs) == 1:
                if seen <= 0:
                    return rf(init, xs[0])
                seen -= 1
                return init
            raise TypeError(
                f"Some arities of transducing `drop` not supported ({1 + len(xs)})."
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

    def xform(rf):
        s = set()

        def rf2(init, *xs):
            nonlocal s
            if not xs:
                return rf(init)
            elif len(xs) == 1:
                x = xs[0]
                if x not in s:
                    s.add(x)
                    return rf(init, x)
                return init
            raise TypeError(
                f"Some arities of transducing `distinct` not supported ({1 + len(xs)})."
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

    def xform(rf):
        stub = object()
        last = stub

        def rf2(init, *xs):
            nonlocal last
            if not xs:
                return rf(init)
            elif len(xs) == 1:
                x = xs[0]
                if last is stub or x != last:
                    last = x
                    return rf(init, x)
                return init
            raise TypeError(
                f"Some arities of transducing `distinct` not supported (received {1 + len(xs)})."
            )

        return rf2

    return xform


def __partition_generator(size: int, coll: Iterable) -> Iterable:
    i = 0
    part = []
    for x in coll:
        part.append(x)
        i += 1
        if i == size:
            yield part
            part = []
            i = 0
    if i > 0:
        yield part
        part = []
        i = 0


def partition(size: int, *rest: Iterable):
    """
    Partition iterable into parts of size `size`.
    """
    if rest:
        if len(rest) == 1:
            return __partition_generator(size, rest[0])
        raise TypeError("Can't `drop` on more than one collection.")

    def xform(rf):
        i = 0
        part = []

        def rf2(init, *xs):
            nonlocal i, part
            if not xs:
                if i > 0:
                    res = rf(init, part)
                    part = []
                    i = 0
                    return res
                return rf(init)
            elif len(xs) == 1:
                part.append(xs[0])
                i += 1
                if i == size:
                    res = rf(init, part)
                    part = []
                    i = 0
                    return res
                return init

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


def generate(xform: Fn, coll: Iterable) -> Iterable:
    """
    Returns a generator which transduces the `coll` using `xform`,
    and yields the result.
    """
    f = xform(__safe_completing(lambda x, y: y))
    stub = object()
    init = stub
    for x in iterator(coll):
        init = f(init, x)
        if isinstance(init, Reduced):
            if init.value is not stub:
                yield init.value
            break
        if init is not stub:
            yield init
            init = stub
    init = f(stub)
    if init is not stub:
        yield init


def into(init, *rest):
    """
    Reduces a coll into the `init` collection with `conj`. `init` must support
    `conj`. If a transducing function is provided, applies transducer while reducing
    into `init`.

    Uses a `chunked_conj` if `init` says its immutable, for fewer intermediate
    collections and using the iterable conj (which is assumed to be a more efficient
    way of adding to `init`).
    """
    rf = chunked_conj() if is_immutable(init) else conj
    if len(rest) == 1:
        return reduce(rf, init, rest[0])
    elif len(rest) == 2:
        xform, coll = rest
        return transduce(xform, rf, init, coll)
    else:
        raise TypeError("Can't `into` without a source or with more than one source.")


def into_new(xform: Fn, coll: Coll) -> Coll:
    """
    Transduce `coll` into a new empty coll of the same type, while
    applying transducing funtion `xform` to the sequence.
    """
    return into(empty(coll), xform, coll)


def __concat_generator(colls: Iterable[Iterable]) -> Iterable:
    for coll in colls:
        yield from coll


def concat(*colls: Iterable):
    """
    Concatenate the values from 1 or more colls into a single sequence.
    If no colls are provided, returns a transducer.
    """
    if colls:
        return __concat_generator(colls)

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


def chunked_conj(chunk_size=32) -> Fn:
    """
    Like `conj` but buffers values into chunks and calls `conj` with chunks.

    Returns a function which will conjoin in batches for the specified `chunk_size`.
    To be used with tranducers. Must complete the fuction (call with 1 arg) to
    guarantee the buffer is flushed (i.e. the last chunk is conjoined). 
    This may or may not be more efficient for some collections.

    The returned function should only be used for one transduction; it should not
    be reused or shared.
    """
    i = 0
    buffer: List = []

    def chunking_conj(coll, *xs) -> Coll:
        nonlocal i, buffer

        if xs:
            if len(xs) > (chunk_size - i):
                res = conj(coll, *buffer[:i])
                buffer[:i] = (None for _ in range(i))
                i = 0
                return conj(res, *xs)
            buffer[i : i + len(xs)] = xs
            i += len(xs)
            if i == chunk_size:
                res = conj(coll, *buffer[:i])
                buffer[:i] = (None for _ in range(i))
                i = 0
                return res
            return coll

        res = conj(coll, *buffer[:i])
        buffer[:i] = (None for _ in range(i))
        i = 0
        return res

    return chunking_conj


# extend collection protocol for built in list, set, dict, str
collection.extend(
    list,
    ("conj_one", lambda l, x: l.append(x) or l),
    ("conj_iterable", lambda l, iterable: l.extend(iterable) or l),
    ("is_immutable", lambda _: False),
    ("empty", lambda _: []),
)

collection.extend(
    set,
    ("conj_one", lambda s, x: s.add(x) or s),
    ("conj_iterable", lambda s, iterable: s.update(iterable) or s),
    ("is_immutable", lambda _: False),
    ("empty", lambda _: set()),
)

collection.extend(
    dict,
    ("conj_one", lambda d, t: d.update([t]) or d),
    ("conj_iterable", lambda d, iterable: d.update(iterable) or d),
    ("is_immutable", lambda _: False),
    ("empty", lambda _: {}),
)

collection.extend(
    str,
    ("conj_one", lambda s, x: s + x),
    ("conj_iterable", lambda s, iterable: "".join(x for x in concat([s], iterable))),
    ("is_immutable", lambda _: True),
    ("empty", lambda _: ""),
)

collection.extend(
    frozenset,
    ("conj_one", lambda fs, x: fs.union([x])),
    ("conj_iterable", lambda fs, iterable: fs.union(iterable)),
    ("is_immutable", lambda _: True),
    ("empty", lambda _: frozenset()),
)

# use dict.items as the iterator accessor for built in dict
# (lets us transduce from one dict into another dict)
custom_iter.extend(dict, ("iter", lambda d: d.items()))
