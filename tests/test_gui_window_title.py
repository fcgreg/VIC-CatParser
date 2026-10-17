"""Tests for the GUI window title version (issue #8)."""

import unittest

from gui.app import WINDOW_TITLE
from vic_catparser import APP_TITLE, __version__


class WindowTitleTests(unittest.TestCase):
    def test_window_title_includes_version(self):
        self.assertEqual(WINDOW_TITLE, APP_TITLE)
        self.assertEqual(WINDOW_TITLE, f"Project VIC Category Parser v{__version__}")


if __name__ == "__main__":
    unittest.main()
