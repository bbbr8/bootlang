# Bootlang

A portable edition of the terms command. Compare the same speaker across two named periods in a supplied JSON array. Each row has speaker, period and text fields. The command reports raw term counts, changes in token share and base-two Jensen-Shannon divergence. Zero means identical token distributions and one means disjoint vocabularies. It measures vocabulary, without attributing intent.

    python bootlang.py terms example.json --speaker pilot --a first --b second
    python -m unittest
