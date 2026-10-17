"""Tests for CLI version output (issue #10)."""

import io
import unittest
from contextlib import redirect_stdout

from vic_catparser import APP_TITLE, __version__
from vic_catparser.cli import build_arg_parser


class CliVersionTests(unittest.TestCase):
    def test_help_includes_version_and_version_option(self):
        buf = io.StringIO()
        with self.assertRaises(SystemExit) as caught:
            with redirect_stdout(buf):
                build_arg_parser().parse_args(["-h"])
        self.assertEqual(caught.exception.code, 0)
        help_text = buf.getvalue()
        self.assertIn(APP_TITLE, help_text)
        self.assertIn(f"v{__version__}", help_text)
        self.assertIn("-v, --version", help_text)

    def test_version_flags_print_title_and_exit(self):
        for flag in ("-v", "--version"):
            with self.subTest(flag=flag):
                buf = io.StringIO()
                with self.assertRaises(SystemExit) as caught:
                    with redirect_stdout(buf):
                        build_arg_parser().parse_args([flag])
                self.assertEqual(caught.exception.code, 0)
                self.assertEqual(buf.getvalue().strip(), APP_TITLE)


if __name__ == "__main__":
    unittest.main()
