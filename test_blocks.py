import itertools
import random
import unittest
from bootlang import terms, permutation_test


class BlockPermutation(unittest.TestCase):
    def rows(self):
        return [dict(speaker='s',period=p,text=t,session=g) for g,p,t in
                [('x','a','red'),('x','b','blue'),('y','a','red red'),('y','b','green')]]

    def test_exact_against_explicit_four_assignments(self):
        rows=self.rows();observed=terms(rows,'s','a','b')['js_divergence_bits'];extreme=0
        for first,second in itertools.product([0,1],[2,3]):
            trial=[dict(row,period='a' if i in [first,second] else 'b') for i,row in enumerate(rows)]
            extreme+=terms(trial,'s','a','b')['js_divergence_bits']>=observed-1e-12
        result=permutation_test(rows,'s','a','b',block='session')
        self.assertEqual((result['partitions'],result['evaluated'],result['p_value']),(4,4,extreme/4))
        self.assertEqual(result['blocking']['period_counts'],[[1,1],[1,1]])

    def test_confounding_fixed_groups_cannot_be_globally_shuffled(self):
        rows=[dict(speaker='s',period=p,text=t,session=g) for g,p,t in
              [('x','a','red'),('x','a','red'),('y','b','blue'),('y','b','blue')]]
        blocked=permutation_test(rows,'s','a','b',block='session')
        self.assertEqual((blocked['partitions'],blocked['p_value']),(1,1))
        self.assertEqual(permutation_test(rows,'s','a','b')['p_value'],1/3)

    def test_seed_and_order_contract(self):
        rows=self.rows();one=permutation_test(rows,'s','a','b',budget=2,seed=9,block='session')
        self.assertEqual(one,permutation_test(rows,'s','a','b',budget=2,seed=9,block='session'))
        expected=permutation_test(rows,'s','a','b',block='session');random.Random(3).shuffle(rows)
        self.assertEqual(expected,permutation_test(rows,'s','a','b',block='session'))

    def test_missing_blocks_rejected_and_other_speaker_ignored(self):
        rows=self.rows();rows.append(dict(speaker='other',period='a',text='ignored'))
        self.assertEqual(permutation_test(rows,'s','a','b',block='session')['utterances'],4)
        rows[0].pop('session')
        with self.assertRaises(ValueError):permutation_test(rows,'s','a','b',block='session')
