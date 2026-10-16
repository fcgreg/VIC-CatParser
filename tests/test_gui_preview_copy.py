"""Tests for Match Preview table clipboard formatting (issue #2 step 2)."""

import unittest
from unittest.mock import MagicMock

from gui.app import VICCatParserApp


class PreviewCopyFormattingTests(unittest.TestCase):
    def test_format_preview_selection_tsv(self):
        app = VICCatParserApp.__new__(VICCatParserApp)
        tree = MagicMock()
        tree.selection.return_value = ("r1", "r2")
        tree.item.side_effect = lambda item_id, key: {
            "r1": ("1", "0", "AAA", "BBB"),
            "r2": ("2", "0", "CCC", "DDD"),
        }[item_id]
        app.preview_tree = tree

        text = VICCatParserApp._format_preview_selection(app)
        self.assertEqual(text, "1\t0\tAAA\tBBB\n2\t0\tCCC\tDDD")

        with_headers = VICCatParserApp._format_preview_selection(app, include_headers=True)
        self.assertEqual(
            with_headers,
            "MediaID\tCategory\tMD5\tSHA1\n1\t0\tAAA\tBBB\n2\t0\tCCC\tDDD",
        )

    def test_format_preview_selection_empty(self):
        app = VICCatParserApp.__new__(VICCatParserApp)
        tree = MagicMock()
        tree.selection.return_value = ()
        app.preview_tree = tree
        self.assertEqual(VICCatParserApp._format_preview_selection(app), "")


if __name__ == "__main__":
    unittest.main()
