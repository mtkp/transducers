import unittest

import transducers.utils as u


class UtilsTests(unittest.TestCase):
    def test_invert_dict(self):
        d = {}
        di = u.invert_dict(d)

        # inverted map is a shallow copy
        self.assertFalse(di is d)

        # assert keys and values are inverted
        d = {"a": 1, "b": 2, "c": 3, "d": 4}
        di = u.invert_dict(d)
        self.assertEqual({"a": 1, "b": 2, "c": 3, "d": 4}, d)
        self.assertEqual({1: "a", 2: "b", 3: "c", 4: "d"}, di)

        # roundtrip test for simple map
        self.assertEqual(d, u.invert_dict(u.invert_dict(d)))

        # value must be hashable to become a key
        d = {"a": [1, 2]}
        self.assertRaises(TypeError, u.invert_dict, d)

    def test_dict_map(self):
        d = dict(zip("abcd", range(4)))
        d2 = u.map_keys(lambda k: k.upper(), d)

        self.assertTrue(d2 is not d)
        self.assertEqual({"a": 0, "b": 1, "c": 2, "d": 3}, d)
        self.assertEqual({"A": 0, "B": 1, "C": 2, "D": 3}, d2)

        d3 = u.map_vals(lambda v: v + 10, d)
        self.assertEqual({"a": 10, "b": 11, "c": 12, "d": 13}, d3)

        d4 = u.map_kvs(lambda k: k + k, lambda v: v * v, d)
        self.assertEqual({"aa": 0, "bb": 1, "cc": 4, "dd": 9}, d4)

    def test_group_by(self):
        a1 = {"a": "a1", "b": 0}
        a2 = {"a": "a2", "b": 1}
        a3 = {"a": "a3", "b": 2}
        a4 = {"a": "a4", "b": 3}
        a5 = {"a": "a5", "b": 2}
        a6 = {"a": "a6", "b": 0}
        coll = [a1, a2, a3, a4, a5, a6]

        groups = u.group_by(lambda d: d["b"], coll)
        self.assertEqual({0: [a1, a6], 1: [a2], 2: [a3, a5], 3: [a4]}, groups)

        groups = u.group_by(lambda d: d["a"], coll)
        self.assertEqual(
            {"a1": [a1], "a2": [a2], "a3": [a3], "a4": [a4], "a5": [a5], "a6": [a6]},
            groups,
        )

        groups = u.group_by(lambda d: d.get("z"), coll)
        self.assertEqual({None: [a1, a2, a3, a4, a5, a6]}, groups)

    def test_group_by_numbers(self):
        nums = range(10)
        groups = u.group_by(lambda x: x % 2 == 0, nums)
        evens = groups[True]
        odds = groups[False]

        # groups are stored in standard python lists
        self.assertTrue(isinstance(evens, list))
        self.assertTrue(isinstance(odds, list))

        self.assertEqual([0, 2, 4, 6, 8], evens)
        self.assertEqual([1, 3, 5, 7, 9], odds)

    def test_index(self):
        nums = range(100)
        index = u.index(lambda x: x % 2 == 0, nums)

        self.assertEqual({True: 98, False: 99}, index)
