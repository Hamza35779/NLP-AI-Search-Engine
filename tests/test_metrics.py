"""Unit tests for the IR metric helpers."""

from src.metrics import (
    average_precision,
    mean_average_precision,
    mean_reciprocal_rank,
    ndcg_at_k,
    precision_at_k,
    recall_at_k,
    reciprocal_rank,
)


def test_precision_and_recall_at_k():
    ranked = [1, 2, 3, 4, 5]
    relevant = {2, 4, 6}
    assert precision_at_k(ranked, relevant, 4) == 0.5
    assert abs(recall_at_k(ranked, relevant, 4) - (2 / 3)) < 1e-9


def test_average_precision_perfect_and_partial():
    assert average_precision([1, 2, 3], {1, 2, 3}) == 1.0
    ap = average_precision([1, 4, 2, 5, 3], {1, 2, 3})
    # Hits at ranks 1, 3, 5 => (1/1 + 2/3 + 3/5) / 3
    assert abs(ap - ((1 + 2 / 3 + 3 / 5) / 3)) < 1e-9


def test_map_returns_mean_of_aps():
    rankings = [[1, 2, 3], [4, 5, 6]]
    rels = [{1}, {6}]
    assert abs(mean_average_precision(rankings, rels) - ((1.0 + 1 / 3) / 2)) < 1e-9


def test_reciprocal_rank_and_mrr():
    assert reciprocal_rank([1, 2, 3], {3}) == 1 / 3
    assert reciprocal_rank([1, 2, 3], {99}) == 0.0
    rrs = mean_reciprocal_rank([[1, 2], [3, 4]], [{2}, {3}])
    assert abs(rrs - ((0.5 + 1.0) / 2)) < 1e-9


def test_ndcg_perfect_ranking_is_one():
    relevance_map = {1: 3, 2: 2, 3: 1}
    assert ndcg_at_k([1, 2, 3], relevance_map, 3) == 1.0


def test_ndcg_handles_empty_relevance():
    assert ndcg_at_k([1, 2, 3], {}, 3) == 0.0
