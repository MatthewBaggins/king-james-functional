from collections import Counter, defaultdict

MarkovChain = defaultdict[tuple[str, ...], Counter[str]]
TokseqsPresentPerDoc = list[set[tuple[str, ...]]]
