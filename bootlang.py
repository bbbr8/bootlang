"""Compare one speaker's vocabulary across two explicitly selected periods."""
import argparse
import json
import math
import re
from collections import Counter
from pathlib import Path


def terms(rows, speaker, a, b):
    if a == b:
        raise ValueError("Select two distinct periods")
    counts = {a: Counter(), b: Counter()}
    for row in rows:
        if row["speaker"] == speaker and row["period"] in counts:
            counts[row["period"]].update(re.findall(r"[^\W\d_]+", row["text"].casefold()))
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


def permutation_test(rows, speaker, a, b, budget=1000, seed=0):
    """Shuffle whole utterances, preserving the observed period sizes."""
    from itertools import combinations
    from random import Random

    if budget < 1:
        raise ValueError("Budget must be positive")
    selected = [r for r in rows if r["speaker"] == speaker and r["period"] in (a,b)
                and re.search(r"[^\W\d_]", r["text"])]
    observed = terms(selected, speaker, a, b)["js_divergence_bits"]
    n = len(selected)
    k = sum(r["period"] == a for r in selected)
    population = math.comb(n, k)
    exact = population <= budget
    rng = Random(seed)
    partitions = (combinations(range(n), k) if exact else
                  (rng.sample(range(n), k) for _ in range(budget)))
    exceed = draws = 0
    for partition in partitions:
        first = set(partition)
        trial = [dict(row, period=a if i in first else b) for i, row in enumerate(selected)]
        score = terms(trial, speaker, a, b)["js_divergence_bits"]
        exceed += score >= observed - 1e-12
        draws += 1
    return dict(observed_bits=observed, utterances=n, partitions=population,
                evaluated=draws, method="exact" if exact else "monte_carlo",
                seed=None if exact else seed, extreme=exceed,
                p_value=exceed/draws if exact else (exceed+1)/(draws+1))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["terms", "permutation"])
    parser.add_argument("input", type=Path)
    for flag in ("speaker", "a", "b"):
        parser.add_argument("--" + flag, required=True)
    parser.add_argument("--budget", type=int, default=1000)
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()
    try:
        rows = json.loads(args.input.read_text(encoding="utf8"))
        params = (rows, args.speaker, args.a, args.b)
        result = (terms(*params) if args.command == "terms" else
                  permutation_test(*params, args.budget, args.seed))
        print(json.dumps(result, indent=2))
    except (ValueError, OSError, KeyError, TypeError) as error:
        parser.exit(2, f"Input error: {error}\n")
