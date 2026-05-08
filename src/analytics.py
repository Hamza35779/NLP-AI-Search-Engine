"""Search analytics tracking."""

from __future__ import annotations

import json
import os
import time
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional


@dataclass
class QueryRecord:
    """Record of a single search query."""
    query: str
    model: str
    num_results: int
    response_time: float
    timestamp: float
    clicked_doc_id: Optional[int] = None


class SearchAnalytics:
    """Track and analyze search queries."""

    def __init__(self, max_records: int = 10000) -> None:
        self.max_records = max_records
        self.records: List[QueryRecord] = []
        self._query_counts: Counter = Counter()
        self._query_times: Dict[str, List[float]] = defaultdict(list)

    def record_query(
        self,
        query: str,
        model: str,
        num_results: int,
        response_time: float,
    ) -> None:
        """Record a search query."""
        record = QueryRecord(
            query=query,
            model=model,
            num_results=num_results,
            response_time=response_time,
            timestamp=time.time(),
        )
        self.records.append(record)

        # Update query counts
        self._query_counts[query] += 1
        self._query_times[query].append(response_time)

        # Trim if needed
        if len(self.records) > self.max_records:
            removed = self.records.pop(0)
            self._query_counts[removed.query] -= 1
            if self._query_counts[removed.query] <= 0:
                del self._query_counts[removed.query]
                del self._query_times[removed.query]

    def record_click(self, query: str, doc_id: int) -> None:
        """Record a click on a search result."""
        for record in reversed(self.records):
            if record.query == query and record.clicked_doc_id is None:
                record.clicked_doc_id = doc_id
                break

    def get_top_queries(self, limit: int = 10) -> List[Dict[str, object]]:
        """Get the most popular queries."""
        return [
            {"query": query, "count": count}
            for query, count in self._query_counts.most_common(limit)
        ]

    def get_stats(self) -> Dict[str, object]:
        """Get overall statistics."""
        if not self.records:
            return {
                "total_queries": 0,
                "unique_queries": 0,
                "avg_response_time": 0,
                "queries_today": 0,
            }

        total = len(self.records)
        unique = len(self._query_counts)
        avg_time = sum(r.response_time for r in self.records) / total

        # Count queries today
        today = datetime.now().date()
        queries_today = sum(
            1 for r in self.records
            if datetime.fromtimestamp(r.timestamp).date() == today
        )

        return {
            "total_queries": total,
            "unique_queries": unique,
            "avg_response_time": round(avg_time, 4),
            "queries_today": queries_today,
        }

    def get_slow_queries(self, threshold: float = 1.0, limit: int = 10) -> List[Dict[str, object]]:
        """Get queries that were slow."""
        slow = [
            {
                "query": r.query,
                "response_time": round(r.response_time, 4),
                "model": r.model,
            }
            for r in self.records
            if r.response_time > threshold
        ]
        slow.sort(key=lambda x: x["response_time"], reverse=True)
        return slow[:limit]

    def get_related_queries(self, query: str, limit: int = 5) -> List[str]:
        """Find queries related to the given query."""
        query_terms = set(query.lower().split())
        if not query_terms:
            return []

        related = []
        for q, count in self._query_counts.most_common():
            if q == query:
                continue
            q_terms = set(q.lower().split())
            overlap = len(query_terms & q_terms)
            if overlap > 0:
                related.append((q, overlap, count))

        related.sort(key=lambda x: (x[1], x[2]), reverse=True)
        return [q for q, _, _ in related[:limit]]

    def save(self, path: str) -> None:
        """Save analytics to disk."""
        data = {
            "records": [
                {
                    "query": r.query,
                    "model": r.model,
                    "num_results": r.num_results,
                    "response_time": r.response_time,
                    "timestamp": r.timestamp,
                    "clicked_doc_id": r.clicked_doc_id,
                }
                for r in self.records
            ],
        }
        with open(path, "w") as f:
            json.dump(data, f)

    def load(self, path: str) -> None:
        """Load analytics from disk."""
        if not os.path.exists(path):
            return
        with open(path, "r") as f:
            data = json.load(f)
        self.records = [
            QueryRecord(
                query=r["query"],
                model=r["model"],
                num_results=r["num_results"],
                response_time=r["response_time"],
                timestamp=r["timestamp"],
                clicked_doc_id=r.get("clicked_doc_id"),
            )
            for r in data.get("records", [])
        ]
        # Rebuild counters
        self._query_counts = Counter(r.query for r in self.records)
        self._query_times = defaultdict(list)
        for r in self.records:
            self._query_times[r.query].append(r.response_time)
