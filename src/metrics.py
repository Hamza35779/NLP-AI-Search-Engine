"""Metrics collection for monitoring and IR evaluation."""

from __future__ import annotations

import math
import time
from typing import Dict, List, Sequence, Set


# --- IR Evaluation Metrics (existing) ---

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
    rankings: List[Sequence[int]],
    relevants: List[Set[int]],
) -> float:
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
    rankings: List[Sequence[int]],
    relevants: List[Set[int]],
) -> float:
    if not rankings:
        return 0.0
    rrs = [reciprocal_rank(r, rel) for r, rel in zip(rankings, relevants)]
    return sum(rrs) / len(rrs)


def dcg_at_k(relevances: List[float], k: int) -> float:
    """Discounted cumulative gain."""
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
    """Normalized DCG."""
    relevances = [float(relevance_map.get(doc_id, 0.0)) for doc_id in ranked[:k]]
    ideal = sorted(relevance_map.values(), reverse=True)[:k]
    dcg = dcg_at_k(relevances, k)
    idcg = dcg_at_k([float(x) for x in ideal], k)
    return dcg / idcg if idcg > 0 else 0.0


# --- SearchMetrics for monitoring ---

class SearchMetrics:
    """Collect and expose metrics for monitoring."""

    def __init__(self):
        self._search_count = 0
        self._cache_hits = 0
        self._cache_misses = 0
        self._error_count = 0
        self._response_times: List[float] = []
        self._start_time = time.time()

    def record_search(self, response_time: float, cache_hit: bool):
        self._search_count += 1
        if cache_hit:
            self._cache_hits += 1
        else:
            self._cache_misses += 1
        self._response_times.append(response_time)
        if len(self._response_times) > 1000:
            self._response_times.pop(0)

    def record_error(self):
        self._error_count += 1

    def get_prometheus_metrics(self) -> str:
        """Export in Prometheus format."""
        cache_hit_rate = (self._cache_hits / max(1, self._search_count)) * 100
        avg_response = sum(self._response_times) / max(1, len(self._response_times))

        return f"""# HELP search_engine_searches_total Total number of searches
# TYPE search_engine_searches_total counter
search_engine_searches_total {self._search_count}

# HELP search_engine_cache_hit_rate Cache hit rate percentage
# TYPE search_engine_cache_hit_rate gauge
search_engine_cache_hit_rate {cache_hit_rate:.2f}

# HELP search_engine_response_time_avg Average response time in seconds
# TYPE search_engine_response_time_avg gauge
search_engine_response_time_avg {avg_response:.4f}

# HELP search_engine_errors_total Total number of errors
# TYPE search_engine_errors_total counter
search_engine_errors_total {self._error_count}

# HELP search_engine_uptime_seconds Uptime in seconds
# TYPE search_engine_uptime_seconds gauge
search_engine_uptime_seconds {time.time() - self._start_time:.0f}
"""

    def get_json_metrics(self) -> Dict:
        """Export as JSON."""
        return {
            "searches_total": self._search_count,
            "cache_hits": self._cache_hits,
            "cache_misses": self._cache_misses,
            "cache_hit_rate": round(
                self._cache_hits / max(1, self._search_count) * 100, 2
            ),
            "errors_total": self._error_count,
            "avg_response_time": round(
                sum(self._response_times) / max(1, len(self._response_times)), 4
            ),
            "uptime_seconds": round(time.time() - self._start_time),
            "response_time_p95": self._percentile(95),
            "response_time_p99": self._percentile(99),
        }

    def _percentile(self, pct: float) -> float:
        if not self._response_times:
            return 0.0
        sorted_times = sorted(self._response_times)
        idx = int(len(sorted_times) * pct / 100)
        return round(sorted_times[min(idx, len(sorted_times) - 1)], 4)
