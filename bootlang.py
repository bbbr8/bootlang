"""Compare one speaker's vocabulary across two explicitly selected periods."""
import argparse
import json
import math
import re
from collections import Counter
from pathlib import Path


def _selected(rows,speaker,a,b):
    if not isinstance(rows,list):raise ValueError('Rows must be a list of utterance objects')
    if any(not isinstance(x,str) or not x for x in (speaker,a,b)):raise ValueError('Speaker and period IDs must be nonempty text')
    if a == b:
        raise ValueError("Select two distinct periods")
    selected=[]
    for row in rows:
        if not isinstance(row,dict) or any(not isinstance(row.get(k),str) for k in ('speaker','period','text')):
            raise ValueError('Rows need speaker, period and text strings')
        if row['speaker']==speaker and row['period'] in (a,b):
            words=Counter(re.findall(r"[^\W\d_]+",row['text'].casefold()))
            if words:selected.append((row,words))
    return selected


def _summary(counts,a,b):
    totals = {p: sum(c.values()) for p, c in counts.items()}
    if not all(totals.values()):
        raise ValueError("Both periods need words from the selected speaker")
    shifts = []
    divergence = 0.0
    for word in sorted(counts[a].keys() | counts[b].keys()):
        before, after = counts[a][word], counts[b][word]
        x, y = before / totals[a], after / totals[b]
        mean = (x + y) / 2
        divergence += sum(v * math.log2(v / mean) / 2 for v in (x, y) if v)
        shifts.append(dict(word=word, before=before, after=after, share_change=y-x))
    return dict(tokens=totals, js_divergence_bits=divergence,
                shifts=sorted(shifts, key=lambda r: -abs(r["share_change"])))


def terms(rows,speaker,a,b):
    selected=_selected(rows,speaker,a,b)
    counts={a:Counter(),b:Counter()}
    for row,words in selected:counts[row['period']].update(words)
    return _summary(counts,a,b)


def permutation_test(rows, speaker, a, b, budget=1000, seed=0, block=None):
    """Shuffle utterances globally or within explicitly supplied exchangeability blocks.

    Block membership is supplied by the caller, never inferred. Each block keeps
    its observed period counts. Dependence within those blocks can still violate
    exchangeability; the result states the permutation design it actually used.
    """
    from itertools import combinations, product
    from random import Random

    if type(budget) is not int or not 1 <= budget <= 100000:
        raise ValueError("Budget must be an integer from 1 to 100000")
    if block is not None and (not isinstance(block, str) or not block):
        raise ValueError('Block must name a row field')
    tokenized=_selected(rows,speaker,a,b)
    selected=[row for row,words in tokenized]
    counts={a:Counter(),b:Counter()}
    for row,words in tokenized:counts[row['period']].update(words)
    observed = _summary(counts,a,b)["js_divergence_bits"]
    n = len(selected)
    k = sum(r["period"] == a for r in selected)
    groups = {}
    for i, row in enumerate(selected):
        key = row.get(block) if block is not None else 'all'
        if block is not None and (type(key) not in (str,int) or key == ''):
            raise ValueError('Every selected utterance needs a nonempty string or integer block ID')
        groups.setdefault((type(key).__name__,key), []).append(i)
    strata = [(indices, sum(selected[i]['period'] == a for i in indices))
              for _,indices in sorted(groups.items())]
    population = math.prod(math.comb(len(indices), count) for indices,count in strata)
    exact = population <= budget
    rng = Random(seed)
    if exact:
        partitions = (tuple(i for group in groups for i in group)
                      for groups in product(*(combinations(indices,count) for indices,count in strata)))
    else:
        partitions = (tuple(i for indices,count in strata for i in rng.sample(indices,count))
                      for _ in range(budget))
    exceed = draws = 0
    for partition in partitions:
        first = set(partition)
        trial={a:Counter(),b:Counter()}
        for i,(_,words) in enumerate(tokenized):trial[a if i in first else b].update(words)
        score = _summary(trial,a,b)["js_divergence_bits"]
        exceed += score >= observed - 1e-12
        draws += 1
    result = dict(observed_bits=observed, utterances=n, partitions=population,
                evaluated=draws, method="exact" if exact else "monte_carlo",
                seed=None if exact else seed, extreme=exceed,
                p_value=exceed/draws if exact else (exceed+1)/(draws+1))
    movable=[indices for indices,count in strata if 0<count<len(indices)]
    result['design']={'informative':population>1,'movable_blocks':len(movable),
                      'movable_utterances':sum(map(len,movable)),
                      'fixed_utterances':n-sum(map(len,movable)),
                      'tokenization':'Unicode casefold followed by alphabetic word matching'}
    if block is not None:
        result['blocking'] = {'field':block,'blocks':len(strata),
                              'period_counts':[[count,len(indices)-count] for indices,count in strata],
                              'assumption':'period labels exchangeable within each supplied block'}
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["terms", "permutation"])
    parser.add_argument("input", type=Path)
    for flag in ("speaker", "a", "b"):
        parser.add_argument("--" + flag, required=True)
    parser.add_argument("--budget", type=int, default=1000)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument('--block', help='Preserve period counts inside this explicitly supplied row field')
    args = parser.parse_args()
    try:
        rows = json.loads(args.input.read_text(encoding="utf8"))
        params = (rows, args.speaker, args.a, args.b)
        result = (terms(*params) if args.command == "terms" else
                  permutation_test(*params, args.budget, args.seed, args.block))
        print(json.dumps(result, indent=2))
    except (ValueError, OSError, KeyError, TypeError) as error:
        parser.exit(2, f"Input error: {error}\n")
