import unittest
from bootlang import permutation_test


class PermutationTests(unittest.TestCase):
    def test_budget_contract(self):
        rows = [dict(period=p, speaker='a', text=p) for p in ['red','blue']]
        for budget in (True, False, 0, -1, 1.5, '10', None):
            with self.subTest(budget=budget), self.assertRaises(ValueError):
                permutation_test(rows, 'a', 'red', 'blue', budget=budget)

    def test_exact_and_seeded(self):
        rows = [dict(period=p, speaker="a", text=p) for p in ["red","red","blue","blue"]]
        args = rows, "a", "red", "blue"
        exact = permutation_test(*args)
        self.assertEqual((exact["partitions"], exact["extreme"], exact["p_value"]), (6,2,1/3))
        self.assertEqual(permutation_test(*args,2,5), permutation_test(*args,2,5))
        self.assertEqual(permutation_test(*args,2,5)["method"], "monte_carlo")

    def test_word_tail_probabilities_match_independent_enumeration(self):
        from fractions import Fraction
        from itertools import combinations
        words = ['red', 'red', 'blue', 'green', 'gold', 'gold']
        rows = [dict(period='a' if i < 3 else 'b', speaker='s', text=w)
                for i, w in enumerate(words)]
        def gap(first, word):
            a = sum(words[i] == word for i in first)
            return abs(Fraction(2 * a - words.count(word), 3))
        partitions = list(combinations(range(6), 3))
        report = permutation_test(rows, 's', 'a', 'b', word_tests=True)
        tests = report['word_tests']
        self.assertEqual(set(words), {x['word'] for x in tests})
        for row in tests:
            w = row['word']
            observed = gap((0, 1, 2), w)
            raw = sum(gap(p, w) >= observed for p in partitions)
            adjusted = sum(max(gap(p, v) for v in words) >= observed for p in partitions)
            self.assertEqual(row['p_value'], raw / 20)
            self.assertEqual(row['max_adjusted_p_value'], adjusted / 20)
        self.assertTrue(any(t['max_adjusted_p_value'] > t['p_value'] for t in tests))

    def test_word_scores_share_blocked_draws_and_sampling_correction(self):
        rows = [dict(period=p, speaker='s', text=t, block=i // 2)
                for i, (p, t) in enumerate([('a', 'red red'), ('b', 'blue')] * 4)]
        plain = permutation_test(rows, 's', 'a', 'b', 7, 41, 'block')
        report = permutation_test(rows, 's', 'a', 'b', 7, 41, 'block', word_tests=True)
        self.assertEqual(plain, {k: v for k, v in report.items() if k != 'word_tests'})
        for item in report['word_tests']:
            self.assertEqual(item['p_value'], (item['extreme'] + 1) / 8)
            self.assertGreaterEqual(item['max_adjusted_p_value'], item['p_value'])
