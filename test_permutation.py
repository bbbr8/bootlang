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
