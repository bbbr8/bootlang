import copy
import unittest
from bootlang import terms, permutation_test


class PermutationHardening(unittest.TestCase):
    def rows(self):
        return [dict(speaker='s',period=p,text=t,session=g) for p,t,g in
                [('a','\u0345','x'),('b','alpha','x')]]

    def test_casefold_tokens_select_same_utterances(self):
        rows=self.rows()
        self.assertEqual(terms(rows,'s','a','b')['tokens'],{'a':1,'b':1})
        self.assertEqual(permutation_test(rows,'s','a','b')['utterances'],2)

    def test_fixed_blocks_report_uninformative_design(self):
        rows=self.rows();rows[1]['session']='y'
        r=permutation_test(rows,'s','a','b',block='session')
        self.assertFalse(r['design']['informative'])
        self.assertEqual(r['design']['movable_utterances'],0)

    def test_mixed_blocks_and_no_input_mutation(self):
        rows=self.rows();old=copy.deepcopy(rows)
        r=permutation_test(rows,'s','a','b',block='session')
        self.assertTrue(r['design']['informative'])
        self.assertEqual(r['design']['movable_utterances'],2)
        self.assertEqual(rows,old)

    def test_invalid_rows_are_input_errors(self):
        for rows in (None,{},[None],[dict(speaker='s',period='a',text=1)]):
            with self.subTest(rows=rows),self.assertRaises(ValueError):
                permutation_test(rows,'s','a','b')

    def test_positive_control_exact_is_symmetric(self):
        rows=[dict(speaker='s',period=p,text=t) for p,t in [('a','red'),('b','blue')]]
        self.assertEqual(permutation_test(rows,'s','a','b')['p_value'],1)

