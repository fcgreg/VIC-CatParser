"""Tests for selectable GUI result/status text helpers (issue #2 step 1)."""

import unittest

import customtkinter as ctk

from gui.app import VICCatParserApp


class SelectableStatusTextTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = ctk.CTk()
        cls.root.withdraw()

    @classmethod
    def tearDownClass(cls):
        cls.root.destroy()

    def test_set_readonly_textbox_replaces_contents(self):
        box = ctk.CTkTextbox(self.root, height=28, activate_scrollbars=False)
        VICCatParserApp._set_readonly_textbox(box, "Ready")
        VICCatParserApp._set_readonly_textbox(box, "Found 2 matches — saved to /tmp/out.txt")
        self.assertEqual(box.get("1.0", "end-1c"), "Found 2 matches — saved to /tmp/out.txt")

    def test_set_readonly_textbox_supports_selection(self):
        box = ctk.CTkTextbox(self.root, height=28, activate_scrollbars=False)
        VICCatParserApp._set_readonly_textbox(box, "copy me")
        box.tag_add("sel", "1.0", "end-1c")
        self.assertEqual(box.get("sel.first", "sel.last"), "copy me")


if __name__ == "__main__":
    unittest.main()
