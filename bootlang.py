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


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["terms"])
    parser.add_argument("input", type=Path)
    for flag in ("speaker", "a", "b"):
        parser.add_argument("--" + flag, required=True)
    args = parser.parse_args()
    try:
        print(json.dumps(terms(json.loads(args.input.read_text(encoding="utf8")),
                               args.speaker, args.a, args.b), indent=2))
    except (ValueError, OSError, KeyError, TypeError) as error:
        parser.exit(2, f"Input error: {error}\n")
