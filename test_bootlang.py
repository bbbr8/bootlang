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

    def test_nonletter_numbers_separate_words(self):
        rows = [
            {"speaker": "s", "period": "a", "text": "red²blue ½"},
            {"speaker": "s", "period": "b", "text": "RED BLUE"},
        ]
        result = terms(rows, "s", "a", "b")
        self.assertEqual(result["tokens"], {"a": 2, "b": 2})
        self.assertEqual(result["js_divergence_bits"], 0)
