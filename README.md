# Bootlang

`python bootlang.py permutation examples/blocked.json --speaker s --a a --b b --block session`
restricts relabeling to caller-supplied exchangeability groups.
Every group keeps its original period counts. Exact enumeration is used when the
partition count fits the budget; otherwise seeded Monte Carlo uses the same blocked
design. The budget is 1–100,000 permutations. The synthetic example has completely
confounded sessions, so blocked inference returns one admissible partition and
p=1. AI can propose grouping hypotheses; the tool neither infers nor validates
exchangeability from text and makes no intent attribution.

A portable edition of the terms command. Compare the same speaker across two named periods in a supplied JSON array. Each row has speaker, period and text fields. The command reports raw term counts, changes in token share and base-two Jensen-Shannon divergence. Zero means identical token distributions and one means disjoint vocabularies. It measures vocabulary, without attributing intent.

    python bootlang.py terms example.json --speaker pilot --a first --b second
    python -m unittest

## Test a vocabulary shift

    python bootlang.py permutation example.json --speaker pilot --a first --b second --budget 1000 --seed 7

This compares the observed divergence with whole-utterance reassignments under exchangeable period labels. It fixes the number of utterances per period and excludes rows with no word tokens. It enumerates every partition when the budget permits and otherwise samples with a reproducible seed and a plus-one Monte Carlo correction. The result includes the observed score, extreme count, partition count, number evaluated and p-value. Repeated or time-correlated utterances can violate the exchangeability assumption.

## Evaluation hardening

Permutation checks tokenize each selected utterance once using the same Unicode casefold rule as `terms`. `design` reports movable/fixed utterances and whether any label reassignment is possible. A fixed-block p=1 describes the supplied design; it offers no power to distinguish periods.

## Local-only distribution

Run the CLI or Python modules locally. No HTTP endpoint, hosting setup or provider
account is required. [Public distribution policy](PUBLIC_DISTRIBUTION.md).
