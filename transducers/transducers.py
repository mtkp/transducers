from typing import List, Union, Callable, Any, Iterable, Set

from transducers.protocols import protocol, extend_protocol
import transducers.protocols as proto

# types

Coll = Union[list, dict, set]
Fn = Callable[..., Any]

# todo linked list class and support for it


def spy(f):
    """
    Wrap f with debugging output.
    """
    name = f.__name__

    def wrapped(*args, **kwargs):
        pargs = ", ".join(str(arg) for arg in args)
        pkwargs = ", ".join(f"{k}={v}" for k, v in kwargs.items())
        if pargs and pkwargs:
            print(f"{name}({pargs}, {pkwargs})")
        elif pargs:
            print(f"{name}({pargs})")
        elif pkwargs:
            print(f"{name}({pkwargs})")
        else:
            print(f"{name}()")
        res = f(*args, **kwargs)
        print(f"  => {res}")
        return res

    wrapped.__doc__ = f.__doc__
    wrapped.__name__ = name
    return wrapped


# declare a new collection protocol
# TODO so far empty hasn't been used...
protocol("collection", ["conj_one", "empty"])

# extend collection for python list
extend_protocol(
    "collection",
    list,
    ("conj_one", proto.InstanceMethod("append")),
    ("empty", proto.ClassConstructor()),
)

# extend collection for python set
extend_protocol(
    "collection",
    set,
    ("conj_one", proto.InstanceMethod("add")),
    ("empty", proto.ClassConstructor()),
)


def dict_conj(d, kv):
    k, v = kv
    d[k] = v


extend_protocol(
    "collection",
    dict,
    ("conj_one", proto.Callable(dict_conj)),
    ("empty", proto.ClassConstructor()),
)

# extend_protocol(
#     "iterable",
#     list
#     ("get_iterator", proto.InstanceMethod("__iter__"))
# )
#
# extend_protocol(
#     "iterable",
#     set
#     ("get_iterator", proto.InstanceMethod("__iter__"))
# )


def conj(coll, *xs):
    """
    Conjoin the value x onto coll.
    """
    conj_one = proto.get_implementation("collection", "conj_one", coll)
    for x in xs:
        conj_one(x)
    return coll


def empty(coll):
    """
    Get a new empty collection of the same type as coll.
    """
    empty = proto.get_implementation("collection", "empty", coll)
    return empty()


protocol("iterable", ["get_iterator"])
extend_protocol("iterable", dict, ("get_iterator", proto.InstanceMethod("items")))


def get_iterator(coll):
    try:
        get_iterator = proto.get_implementation("iterable", "get_iterator", coll)
        return get_iterator()
    except:
        return iter(coll)


def complement(f):
    def f2(*args):
        return not f(*args)

    return f2


def map(f: Fn, *rest: Iterable):
    if rest:
        if len(rest) == 1:
            return (f(x) for x in get_iterator(rest[0]))
        else:
            return (f(*xs) for xs in zip(*(get_iterator(r) for r in rest)))
    else:

        def xform(rf):
            def rf2(*args):
                if len(args) == 1:
                    return rf(*args)
                elif len(args) == 2:
                    init, x = args
                    return rf(init, f(x))
                raise ValueError(
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
            return (x for x in get_iterator(rest[0]) if pred(x))
        raise ValueError("Can't `filter` on more than one collection.")
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
                raise ValueError(
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


def reduced(value) -> Reduced:
    if isinstance(value, Reduced):
        return value
    return Reduced(value)


def _take_generator(n: int, coll: Iterable):
    """
    Helper function to implement `take` generator.
    """
    for i, x in enumerate(get_iterator(coll)):
        if i < n:
            yield x


def take(n: int, *rest: Iterable):
    if rest:
        if len(rest) == 1:
            return _take_generator(n, rest[0])
        raise ValueError("Can't `take` on more than one collection.")
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
                    return reduced(init)
                raise ValueError(
                    f"Some arities of transducing `take` not yet supported ({args})."
                )

            return rf2

        return xform


def _drop_generator(n: int, coll: Iterable):
    """
    Helper function to implement `drop` generator.
    """
    for i, x in enumerate(get_iterator(coll)):
        if i >= n:
            yield x


def drop(n: int, *rest: Iterable):
    if rest:
        if len(rest) == 1:
            return _drop_generator(n, rest[0])
        raise ValueError("Can't `drop` on more than one collection.")
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
                raise ValueError(
                    f"Some arities of transducing `drop` not yet supported ({args})."
                )

            return rf2

        return xform


def _distinct_generator(coll: Iterable) -> Iterable:
    # not sure why mypy needs a type hint here
    s: Set = set()
    for x in coll:
        if x not in s:
            s.add(x)
            yield x


def distinct(*rest: Iterable):
    if rest:
        if len(rest) == 1:
            return _distinct_generator(rest[0])
        raise ValueError("Can't `drop` on more than one collection.")
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
                raise ValueError(
                    f"Some arities of transducing `distinct` not yet supported ({args})."
                )

            return rf2

        return xform


# TODO
# - mapcat
# - take-while (uses reduced)
# - drop-while
# - take-nth
# - distinct
# - dedupe
# - interpose (uses reduced)
# - partition-all
# - cat ... ?
# - halt-when (uses reduced)


def reduce(f: Fn, init: Union[Coll, Reduced], coll: Iterable):
    for x in get_iterator(coll):
        init = f(init, x)
        if isinstance(init, Reduced):
            init = init.value
            break
    return init


def transduce(xform: Fn, f: Fn, init: Union[Coll, Reduced], coll: Iterable):
    return reduce(xform(f), init, coll)


def into(init: Coll, *rest):
    if len(rest) == 1:
        return reduce(conj, init, rest[0])
    elif len(rest) == 2:
        xform, coll = rest
        return transduce(xform, conj, init, coll)
    else:
        raise ValueError("Can't `into` without a source or with more than one source.")


class Wrapper:
    def __init__(self):
        self.x = None
        self.empty = True

    def push(self, x):
        self.x, self.empty = x, False

    def pop(self):
        x, self.x, self.empty = self.x, None, True
        return x


extend_protocol(
    "collection",
    Wrapper,
    ("conj_one", proto.InstanceMethod("push")),
    ("empty", proto.ClassConstructor()),
)


def generate(xform: Fn, coll: Iterable) -> Iterable:
    f = xform(conj)
    init = Wrapper()
    for x in get_iterator(coll):
        init = f(init, x)
        if isinstance(init, Reduced):
            init = init.value
            if not init.empty:
                yield init.pop()
            return
        elif not init.empty:
            yield init.pop()


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


def add(x, y):
    return x + y


def inc(x: int):
    return x + 1


def positive(x):
    return x > 0


def even(x):
    return x % 2 == 0


if __name__ == "__main__":
    print("take")
    print(f"  {list(take(3, [1, 2, 3, 6, 9, 101]))}")
    print(f"  {list(take(12, [2, 1, 99]))}")
    print()
    print("drop")
    print(f"  {list(drop(3, [1, 2, 3, 6, 9, 101]))}")
    print(f"  {list(drop(12, [2, 1, 99]))}")
    print()
    print("conj")
    print(f"  {conj([], 1, 2, 3, 2, 1)}")
    print(f"  {conj(conj([], 1), 1)}")
    print(f"  {conj(conj(set(), 1), 1, 2, 3, 2)}")
    print()
    print("dict")
    print(f"  {conj({}, (1, 2))}")
    print(f"  {conj(conj({}, (1, 2)), (1, 3))}")
    print(f"  {conj({}, (1, 2), (2, 4), (3, 6))}")
    print(f"  take from a dict {dict(take(2, {1: 1, 2: 2, 3: 3}))}")
    print()
    print("generator")
    mapped_values = map(inc, [1, 2, 5, 7])
    print(f"  {mapped_values} => {list(mapped_values)}")
    mapped_values = map(add, [1, 2, 5, 7], [3, 4, 99])
    print(f"  {mapped_values} => {list(mapped_values)}")
    print()
    print("transducer")
    a_mapper = map(inc)
    print(f"  a mapper => {transduce(a_mapper, conj, [], [9, 10, 11])}")
    print(f"  a mapper => {transduce(a_mapper, conj, [], [11])}")
    print(f"  a mapper => {transduce(a_mapper, conj, [], [])}")
    l = [-1000, -2, -1, 0, 1, 2, 99, 404]
    pos_filter = filter(positive)
    print(f"  a pos filter => {transduce(pos_filter, conj, [], l)}")
    even_filter = filter(even)
    print(f"  an even filter => {transduce(even_filter, conj, [], l)}")
    pos_and_even_filter = comp(filter(positive), filter(even))
    print(f"  even+pos filter => {transduce(pos_and_even_filter, conj, [], l)}")

    inc_pos = comp(filter(positive), map(inc))
    print(f"  increment positives => {transduce(inc_pos, conj, [], l)}")

    pos_inc = comp(map(inc), filter(positive))
    print(f"  positives of increments => {transduce(pos_inc, conj, [], l)}")

    increment_first_few_evens = comp(filter(even), map(inc), take(5))

    print(
        f"  increment first few evens => {into([], increment_first_few_evens, range(20))}"
    )

    print(
        f"  increment first few evens of a very large (lazy) range => {into([], increment_first_few_evens, range(2000000000))}"
    )

    map_then_filter = comp(filter(even), map(inc))
    print(
        f"  map then filter => {transduce(map_then_filter, conj, [], [1, 2, 5, 9, 22, 28])}"
    )
    filter_then_map = comp(map(inc), filter(even))
    print(
        f"  filter then map => {transduce(filter_then_map, conj, [], [1, 2, 5, 9, 22, 28])}"
    )

    filter_then_map2 = comp(filter(complement(even)), map(inc), map(inc))
    print(
        f"  filter then map (odds) => {transduce(filter_then_map2, conj, [], [1, 2, 5, 9, 22, 28])}"
    )

    map5 = comp(map(inc), map(inc), map(inc), map(inc), map(inc))
    print(
        f"  map five times => {transduce(map5, conj, [], [1, 2, 3, 2, 1, 2, 3, 2, 1])}"
    )

    filter_then_take = comp(take(10), filter(even))
    print(
        f"  filter evens then take 10 => {transduce(filter_then_take, conj, [], range(300))}"
    )

    def foo(t1, t2):
        return (t1[0] + t2[0], t1[1] + t2[1])

    print(f"  {dict(map(foo, {1: 2, 3: 4}, {5: 6, 7: 8}))}")
    print(f"  {into([], drop(6), range(15))}")
    print(f"  {into([], comp(drop(6), map(str), take(3)), range(15))}")
    print(
        f"  {into([], comp(remove(lambda n: n is None), take(3)), [None, 1, None, 2, None, 6, None])}"
    )
