"""Evaluate the engine on a tiny labelled query set.

Run from the repository root:

    python examples/eval_demo.py
"""

from __future__ import annotations

import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
sys.path.insert(0, ROOT)

from src.metrics import (
    mean_average_precision,
    mean_reciprocal_rank,
    precision_at_k,
    recall_at_k,
)
from src.search_engine import SearchEngine


# (query, set of relevant doc ids by source filename)
QUERIES = [
    ("information retrieval", {"information_retrieval.txt"}),
    ("machine learning", {"machine_learning.txt", "natural_language_processing.txt"}),
    ("bm25 ranking", {"tf_idf_and_bm25.txt"}),
    ("porter stem", {"porter_stemmer.txt"}),
    ("evaluation metrics", {"evaluation_metrics.txt"}),
]


def _doc_id_set(engine: SearchEngine, sources: set[str]) -> set[int]:
    return {
        doc.doc_id
        for doc in engine.index.all_documents()
        if doc.source in sources
    }


def main() -> int:
    engine = SearchEngine(model="bm25").index_corpus(
        os.path.join(ROOT, "data", "sample_docs")
    )

    rankings: list[list[int]] = []
    relevants: list[set[int]] = []
    rows = []
    for query, gold in QUERIES:
        results = engine.search(query, top_k=10)
        ranked = [r.doc_id for r in results]
        gold_ids = _doc_id_set(engine, gold)

        rankings.append(ranked)
        relevants.append(gold_ids)
        rows.append((query, precision_at_k(ranked, gold_ids, 3), recall_at_k(ranked, gold_ids, 3)))

    print(f"{'Query':<32} {'P@3':>6}  {'R@3':>6}")
    print("-" * 46)
    for q, p, r in rows:
        print(f"{q:<32} {p:6.3f}  {r:6.3f}")

    print()
    print(f"MAP : {mean_average_precision(rankings, relevants):.4f}")
    print(f"MRR : {mean_reciprocal_rank(rankings, relevants):.4f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
