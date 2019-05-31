import unittest

import transducers.utils as utils


class UtilsTests(unittest.TestCase):
    def test_invert_dict(self):
        d = {}
        di = utils.invert_dict(d)

        # inverted map is a shallow copy
        self.assertFalse(di is d)

        # assert keys and values are inverted
        d = {"a": 1, "b": 2, "c": 3, "d": 4}
        di = utils.invert_dict(d)
        self.assertEqual({"a": 1, "b": 2, "c": 3, "d": 4}, d)
        self.assertEqual({1: "a", 2: "b", 3: "c", 4: "d"}, di)

        # roundtrip test for simple map
        self.assertEqual(d, utils.invert_dict(utils.invert_dict(d)))

        # value must be hashable to become a key
        d = {"a": [1, 2]}
        self.assertRaises(TypeError, utils.invert_dict, d)
