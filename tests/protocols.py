import unittest

import transducers.protocols as p


class ProtocolTests(unittest.TestCase):
    def test_protocol(self):
        parens = p.protocol("open_paren", "contents", "close_paren")

        # doesn't support methods that aren't part of protocol's interface
        self.assertRaises(
            AttributeError, parens.__getattribute__, "not_part_of_interface"
        )

        # raises ValueError if the value does not implement the protocol's interface
        self.assertRaises(ValueError, parens.open_paren, list())

        parens.extend(
            list,
            ("open_paren", lambda _: "["),
            ("close_paren", lambda _: "]"),
            ("contents", lambda l: " then ".join(f"{x}" for x in l)),
        )

        def make_pretty(x):
            open = parens.open_paren(x)
            body = parens.contents(x)
            close = parens.close_paren(x)
            return f"{open}{body}{close}"

        self.assertEqual("[1 then 2 then 3]", make_pretty([1, 2, 3]))

        parens.extend(
            type,
            ("open_paren", lambda _: "< ~ "),
            ("close_paren", lambda _: " ~ >"),
            ("contents", lambda t: f"{t.__module__}.{t.__name__}"),
        )
        self.assertEqual(
            "< ~ transducers.protocols.Protocol ~ >", make_pretty(p.Protocol)
        )

    def test_protocol_incomplete(self):
        pass
