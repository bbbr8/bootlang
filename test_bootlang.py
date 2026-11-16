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

class DistributionArithmetic(unittest.TestCase):
    def test_matches_direct_token_pair_enumeration(self):
        from fractions import Fraction
        a, b = ['x','x','y'], ['x','z']
        rows = [dict(period=p, text=' '.join(words), speaker='s') for p,words in [('a',a),('b',b)]]
        result = terms(rows,'s','a','b')
        self.assertEqual(result['total_variation_fraction'], '1/2')
        self.assertEqual(Fraction(result['cross_period_match_fraction']),
                         Fraction(sum(x==y for x in a for y in b), len(a)*len(b)))
        for p, words in [('a',a),('b',b)]:
            pairs = [(x,y) for i,x in enumerate(words) for j,y in enumerate(words) if i!=j]
            self.assertEqual(Fraction(result['within_period_match_fraction'][p]),
                             Fraction(sum(x==y for x,y in pairs),len(pairs)))
        rows[0]['text']='x'
        self.assertIsNone(terms(rows,'s','a','b')['within_period_match_fraction']['a'])
