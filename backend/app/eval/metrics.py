"""Pure retrieval metrics computed at the document level.

``retrieved`` is the ranked list of document identifiers (e.g. filenames) for a
query; ``relevant`` is the set of identifiers considered correct.
"""
from collections.abc import Sequence


def precision_at_k(retrieved: Sequence[str], relevant: set[str], k: int) -> float:
    top_k = retrieved[:k]
    if not top_k:
        return 0.0
    hits = sum(1 for doc in top_k if doc in relevant)
    return hits / len(top_k)


def recall_at_k(retrieved: Sequence[str], relevant: set[str], k: int) -> float:
    if not relevant:
        return 0.0
    top_k = retrieved[:k]
    found = {doc for doc in top_k if doc in relevant}
    return len(found) / len(relevant)


def reciprocal_rank(retrieved: Sequence[str], relevant: set[str]) -> float:
    for rank, doc in enumerate(retrieved, start=1):
        if doc in relevant:
            return 1.0 / rank
    return 0.0
