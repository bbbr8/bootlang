# Bootlang

A portable edition of the terms command. Compare the same speaker across two named periods in a supplied JSON array. Each row has speaker, period and text fields. The command reports raw term counts, changes in token share and base-two Jensen-Shannon divergence. Zero means identical token distributions and one means disjoint vocabularies. It measures vocabulary, without attributing intent.

    python bootlang.py terms example.json --speaker pilot --a first --b second
    python -m unittest

## Test a vocabulary shift

    python bootlang.py permutation example.json --speaker pilot --a first --b second --budget 1000 --seed 7

This compares the observed divergence with whole-utterance reassignments under exchangeable period labels. It fixes the number of utterances per period and excludes rows with no word tokens. It enumerates every partition when the budget permits and otherwise samples with a reproducible seed and a plus-one Monte Carlo correction. The result includes the observed score, extreme count, partition count, number evaluated and p-value. Repeated or time-correlated utterances can violate the exchangeability assumption.
