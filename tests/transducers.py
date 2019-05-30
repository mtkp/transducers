import unittest
import inspect

import transducers.transducers as t


def inc(x):
    return x + 1


def square(x):
    return x ** 2


def add2(x, y):
    return x + y


def add3(x, y, z):
    return x + y + z


def addtup2(t):
    return add2(*t)


class CompTests(unittest.TestCase):
    def test_comp_simple(self):
        f1 = t.comp(inc)
        f2 = t.comp(inc, inc)
        f3 = t.comp(inc, inc, inc)
        f4 = t.comp(inc, inc, inc, inc)
        f5 = t.comp(inc, inc, inc, inc, inc)

        self.assertEqual(43, inc(42))
        self.assertEqual(f1(42), inc(42))
        self.assertEqual(f2(99), inc(inc(99)))
        self.assertEqual(f3(1001), inc(inc(inc(1001))))
        self.assertEqual(f4(77), inc(inc(inc(inc(77)))))
        self.assertEqual(f5(-5), inc(inc(inc(inc(inc(-5))))))

    def test_comp_direction(self):
        square_then_inc = t.comp(inc, square)
        inc_then_square = t.comp(square, inc)
        self.assertEqual(square_then_inc(6), inc(square(6)))
        self.assertEqual(inc_then_square(7), square(inc(7)))
        self.assertNotEqual(square_then_inc(8), inc_then_square(8))

    def test_comp_arity(self):
        f = t.comp(inc, add3)
        self.assertEqual(13, f(3, 4, 5))

        # all composing functions (except for the last) can only accept one argument
        bad_f = t.comp(add3, add3)
        self.assertRaises(TypeError, bad_f, 3, 4, 5)


class ConjTests(unittest.TestCase):
    def test_conj_list(self):
        coll = []
        t.conj(coll, 1)
        self.assertEqual([1], coll)

        # conj also returns the provided coll for chaining
        coll2 = t.conj(coll, 42)
        self.assertEqual([1, 42], coll2)
        self.assertTrue(coll2 is coll)

        # conj supports multiple values
        t.conj(coll, 99, 100, -500, 99, 42)
        self.assertEqual([1, 42, 99, 100, -500, 99, 42], coll)
        self.assertEqual(7, len(coll))

    def test_conj_set(self):
        coll = set()
        t.conj(coll, 1)
        self.assertEqual(set([1]), coll)

        # conj also returns the provided coll for chaining
        coll2 = t.conj(coll, 42)
        self.assertEqual(set([1, 42]), coll2)
        self.assertTrue(coll2 is coll)

        # conj supports multiple values
        t.conj(coll, 99, 100, -500, 99, 42)
        self.assertEqual(set([1, 42, 99, 100, -500]), coll)
        self.assertEqual(5, len(coll))

    def test_conj_dict(self):
        coll = {}
        t.conj(coll, (1, 1))
        self.assertEqual({1: 1}, coll)

        # conj also returns the provided coll for chaining
        coll2 = t.conj(coll, (2, 2))
        self.assertEqual({1: 1, 2: 2}, coll2)
        self.assertTrue(coll2 is coll)

        # conj supports multiple values
        t.conj(coll, (42, 99), (1, 8), (100, -500))
        self.assertEqual({1: 8, 2: 2, 42: 99, 100: -500}, coll)
        self.assertEqual(4, len(coll))


class IteratorTests(unittest.TestCase):
    def test_iterator(self):
        def round_trip(coll):
            return coll.__class__(t.iterator(coll))

        self.assertEqual([1, 2, 3], round_trip([1, 2, 3]))
        self.assertEqual(set([1, 2, 3, 1]), round_trip(set([1, 2, 3, 1])))
        self.assertEqual({1: 2, 3: 4}, round_trip({1: 2, 3: 4}))


class MapTests(unittest.TestCase):
    def test_map(self):
        res = t.map(inc, range(4))
        self.assertTrue(inspect.isgenerator(res))
        self.assertEqual([1, 2, 3, 4], list(res))
        self.assertEqual([], list(res))

        res = t.map(addtup2, {1: 2, 3: 4, 5: 6})
        self.assertTrue(inspect.isgenerator(res))
        self.assertEqual([3, 7, 11], list(res))
        self.assertEqual([], list(res))


class TakeTests(unittest.TestCase):
    def test_take(self):
        res = t.take(5, range(100000000000))
        self.assertTrue(inspect.isgenerator(res))
        self.assertEqual([0, 1, 2, 3, 4], list(res))


class DropTests(unittest.TestCase):
    def test_drop(self):
        res = t.drop(5, range(18))
        self.assertTrue(inspect.isgenerator(res))
        self.assertEqual(list(range(5, 18)), list(res))


class IntoNewTests(unittest.TestCase):
    def test_into_new(self):
        xf = t.comp(
            t.map(square), t.filter(lambda x: x % 3 == 0), t.drop(10), t.take(3)
        )
        numbers_list = list(range(100))
        self.assertEqual([900, 1089, 1296], t.into_new(xf, numbers_list))

        numbers_set = set(range(100, 138))
        self.assertEqual(set([15129, 15876]), t.into_new(xf, numbers_set))

        duplicate_numbers_list = [1, 2, 3, 2, 1, 2, 3, 2, 1]
        self.assertEqual([1, 2, 3], t.into_new(t.distinct(), duplicate_numbers_list))

    def test_into_new_dict(self):
        invert = t.map(lambda t: (t[1], t[0]))
        self.assertEqual(
            {2: 1, 4: 3, 6: 5, 8: 7}, t.into_new(invert, {1: 2, 3: 4, 5: 6, 7: 8})
        )

        mark_empty_strings = t.map(
            lambda t: (t[0], None) if isinstance(t[1], str) and t[1] == "" else t
        )
        remove_nones = t.remove(lambda t: t[1] is None)
        upper_keys = t.map(lambda t: (t[0].upper(), t[1]))
        format_json = t.comp(mark_empty_strings, remove_nones, upper_keys)

        initial_json = {
            "one": 1,
            "four": {},
            "two": None,
            "three": 42,
            "five": None,
            "six": {"hello": "world"},
            "seven": "",
            "eight": 99.9,
        }
        expected_json = {
            "ONE": 1,
            "THREE": 42,
            "FOUR": {},
            "SIX": {"hello": "world"},
            "EIGHT": 99.9,
        }

        self.assertEqual(expected_json, t.into_new(format_json, initial_json))

        # piecewise transformation
        formatted_json_piecewise = initial_json
        for xf in [mark_empty_strings, remove_nones, upper_keys]:
            formatted_json_piecewise = t.into_new(xf, formatted_json_piecewise)

        self.assertEqual(expected_json, formatted_json_piecewise)
