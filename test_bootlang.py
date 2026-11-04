import json
from pathlib import Path
import unittest
from bootlang import terms


class TermsTests(unittest.TestCase):
    def test_disjoint(self):
        rows = json.loads(Path(__file__).with_name("example.json").read_text())
        result = terms(rows, "pilot", "first", "second")
        self.assertEqual(result["tokens"], {"first": 2, "second": 2})
        self.assertEqual(result["js_divergence_bits"], 1.0)

    def test_missing(self):
        with self.assertRaises(ValueError):
            terms([], "pilot", "first", "second")
