"""Evaluation metrics for the search engine.

Provides the standard IR metrics (precision@k, recall@k, average precision,
mean average precision, mean reciprocal rank, nDCG@k). All functions accept
``ranked`` as an iterable of doc IDs in ranked order and ``relevant`` as a
set of doc IDs known to be relevant to the query.
"""

from __future__ import annotations

import math
from typing import Iterable, List, Sequence, Set


def precision_at_k(ranked: Sequence[int], relevant: Set[int], k: int) -> float:
    if k <= 0:
        return 0.0
    top = list(ranked)[:k]
    if not top:
        return 0.0
    hits = sum(1 for d in top if d in relevant)
    return hits / k


def recall_at_k(ranked: Sequence[int], relevant: Set[int], k: int) -> float:
    if k <= 0 or not relevant:
        return 0.0
    top = list(ranked)[:k]
    hits = sum(1 for d in top if d in relevant)
    return hits / len(relevant)


def average_precision(ranked: Sequence[int], relevant: Set[int]) -> float:
    if not relevant:
        return 0.0
    hits = 0
    summed = 0.0
    for i, doc_id in enumerate(ranked, start=1):
        if doc_id in relevant:
            hits += 1
            summed += hits / i
    return summed / len(relevant)


def mean_average_precision(
    rankings: Iterable[Sequence[int]],
    relevants: Iterable[Set[int]],
) -> float:
    rankings = list(rankings)
    relevants = list(relevants)
    if not rankings:
        return 0.0
    aps = [average_precision(r, rel) for r, rel in zip(rankings, relevants)]
    return sum(aps) / len(aps)


def reciprocal_rank(ranked: Sequence[int], relevant: Set[int]) -> float:
    for i, doc_id in enumerate(ranked, start=1):
        if doc_id in relevant:
            return 1.0 / i
    return 0.0


def mean_reciprocal_rank(
    rankings: Iterable[Sequence[int]],
    relevants: Iterable[Set[int]],
) -> float:
    rankings = list(rankings)
    relevants = list(relevants)
    if not rankings:
        return 0.0
    rrs = [reciprocal_rank(r, rel) for r, rel in zip(rankings, relevants)]
    return sum(rrs) / len(rrs)


def dcg_at_k(relevances: List[float], k: int) -> float:
    """Discounted cumulative gain — uses the (2^rel - 1) gain function."""
    relevances = relevances[:k]
    if not relevances:
        return 0.0
    return sum(
        (math.pow(2.0, rel) - 1) / math.log2(i + 2)
        for i, rel in enumerate(relevances)
    )


def ndcg_at_k(
    ranked: Sequence[int],
    relevance_map: dict,
    k: int,
) -> float:
    """Normalized DCG — `relevance_map` maps doc_id -> graded relevance."""
    relevances = [float(relevance_map.get(doc_id, 0.0)) for doc_id in ranked[:k]]
    ideal = sorted(relevance_map.values(), reverse=True)[:k]
    dcg = dcg_at_k(relevances, k)
    idcg = dcg_at_k([float(x) for x in ideal], k)
    return dcg / idcg if idcg > 0 else 0.0
