from transducers import *


def add(x, y):
    return x + y


def inc(x: int):
    return x + 1


def positive(x):
    return x > 0


def even(x):
    return x % 2 == 0


dup_list = [1, 2, 3, 2, 1, 2, 3]
cleaned_list = into_new(distinct(), dup_list)

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
print(f"  map five times => {transduce(map5, conj, [], [1, 2, 3, 2, 1, 2, 3, 2, 1])}")

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
print()
print("generate (kinda like sequence)")
xf = comp(drop(5), map(inc), take(6))
g = generate(xf, range(50))
print(f"  {g}")
print(f"  {list(g)}")
print(f"  {list(generate(take(0), range(2)))}")
print(f"  {list(generate(take(1), range(2)))}")
print(f"  {list(generate(take(2), range(2)))}")
print(f"  {list(generate(take(3), range(2)))}")
