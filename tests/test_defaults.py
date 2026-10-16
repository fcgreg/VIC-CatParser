"""Tests for default CLI/service output options (issue #1)."""

import inspect
import unittest
from pathlib import Path

from vic_catparser.cli import build_arg_parser
from vic_catparser.service import process_vic


class DefaultOptionsTests(unittest.TestCase):
    def test_cli_defaults_are_hashonly_md5(self):
        args = build_arg_parser().parse_args(["sample.json", "1"])
        self.assertEqual(args.output_format, "hashonly")
        self.assertEqual(args.hash, "md5")

    def test_cli_can_override_format_to_json(self):
        args = build_arg_parser().parse_args(["sample.json", "1", "-f", "json"])
        self.assertEqual(args.output_format, "json")
        self.assertEqual(args.hash, "md5")

    def test_cli_can_override_hash_type(self):
        args = build_arg_parser().parse_args(["sample.json", "1", "--hash", "sha1"])
        self.assertEqual(args.output_format, "hashonly")
        self.assertEqual(args.hash, "sha1")

    def test_process_vic_signature_defaults(self):
        params = inspect.signature(process_vic).parameters
        self.assertEqual(params["output_format"].default, "hashonly")
        self.assertEqual(params["hash_type"].default, "md5")

    def test_process_vic_default_emits_md5_hashonly(self):
        sample = Path(__file__).resolve().parents[1] / "utils" / "example-VIC-data.json"
        result = process_vic(sample, category=0, collect_matches=True)
        self.assertEqual(result.matches_found, 2)
        self.assertEqual(result.hash_matches_processed, 2)
        self.assertEqual(result.empty_hash_count, 0)


if __name__ == "__main__":
    unittest.main()
