"""
Paren-aware inline splitting (zOS#82).

A comma inside balanced parentheses is prose, not a delimiter:
    fields: [{name: sector, label: Sector (e.g. Publishing, Music Label)}]
must keep the full label instead of silently truncating at the comma.

Unbalanced parens (smileys, "1)" enumerations) fail open to the historical
behavior so a half-open paren never swallows the rest of the object.
"""

import unittest

from zlsp.parser import loads
from zlsp.parser.basic.value_processors import (
    parens_balanced,
    parse_brace_object,
    parse_bracket_array,
    split_on_comma,
)


class TestParensBalanced(unittest.TestCase):
    def test_balanced(self):
        self.assertTrue(parens_balanced("a (b, c) d"))
        self.assertTrue(parens_balanced("no parens at all"))
        self.assertTrue(parens_balanced("(nested (deep)) ok"))

    def test_unbalanced(self):
        self.assertFalse(parens_balanced("smile :) here"))
        self.assertFalse(parens_balanced("open ( and never close"))
        self.assertFalse(parens_balanced(") before ("))


class TestSplitOnComma(unittest.TestCase):
    def test_issue82_shape(self):
        parts = split_on_comma(
            "name: sector, label: Sector (e.g. Publishing, Music Label), type: text"
        )
        self.assertEqual(
            [p.strip() for p in parts],
            [
                "name: sector",
                "label: Sector (e.g. Publishing, Music Label)",
                "type: text",
            ],
        )

    def test_brackets_still_nest(self):
        self.assertEqual(split_on_comma("a: [1, 2], b: 3"), ["a: [1, 2]", " b: 3"])

    def test_escaped_comma_inside_parens_still_resolves(self):
        # Authors who worked around #82 with the \, escape must not regress
        # to a literal backslash now that parens nest.
        self.assertEqual(split_on_comma("func(x\\, y), other"), ["func(x, y)", " other"])

    def test_escape_preserved_in_nested_array(self):
        # Inside brackets nothing splits and the escape survives for the
        # recursive item parse to resolve
        self.assertEqual(split_on_comma("[[x\\, y], z]"), ["[[x\\, y], z]"])

    def test_unbalanced_parens_fail_open(self):
        # Lone ")" — historical behavior: comma still splits
        self.assertEqual(
            split_on_comma("label: nice :), type: text"),
            ["label: nice :)", " type: text"],
        )
        # Lone "(" — must NOT swallow the rest of the object
        self.assertEqual(
            split_on_comma("label: bad ( case, type: text"),
            ["label: bad ( case", " type: text"],
        )


class TestInlineCollections(unittest.TestCase):
    def test_brace_object_keeps_paren_prose(self):
        obj = parse_brace_object(
            "{name: sector, label: Sector (e.g. Publishing, Music Label), type: text}"
        )
        self.assertEqual(obj["label"], "Sector (e.g. Publishing, Music Label)")
        self.assertEqual(obj["type"], "text")

    def test_bracket_array_keeps_paren_prose(self):
        arr = parse_bracket_array("[Alpha (a, b), Beta]")
        self.assertEqual(arr, ["Alpha (a, b)", "Beta"])

    def test_full_document_issue82(self):
        doc = (
            "Main:\n"
            "  zDialog:\n"
            "    fields: [{name: sector, label: Sector (e.g. Publishing, Music Label), type: text}, {name: notes, type: text}]\n"
        )
        data = loads(doc)
        fields = data["Main"]["zDialog"]["fields"]
        self.assertEqual(len(fields), 2)
        self.assertEqual(fields[0]["label"], "Sector (e.g. Publishing, Music Label)")
        self.assertEqual(fields[1]["name"], "notes")


if __name__ == "__main__":
    unittest.main()
