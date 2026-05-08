"""Use the search engine directly from Python.

Run from the repository root:

    python examples/python_api.py
"""

from __future__ import annotations

import os
import sys

# Make the `src` package importable when running this file directly.
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
sys.path.insert(0, ROOT)

from src.config import EngineConfig
from src.search_engine import SearchEngine


def main() -> int:
    cfg = EngineConfig(bm25_k1=1.4, bm25_b=0.7)
    engine = SearchEngine(cfg, model="bm25")
    engine.index_corpus(os.path.join(ROOT, "data", "sample_docs"))

    print(f"Index ready. Stats: {engine.stats()}\n")

    queries = [
        "machine learning",
        '"natural language" processing',
        "ranking +bm25 -neural",
        "spel sugestion",  # typo, should trigger suggestion
    ]
    for q in queries:
        print(f"Query: {q}")
        results = engine.search(q, top_k=3)
        if not results:
            suggestion = engine.suggest_query(q)
            print(f"  no results — did you mean: {suggestion!r}?")
            if suggestion:
                results = engine.search(suggestion, top_k=3)
        for rank, r in enumerate(results, start=1):
            print(f"  {rank}. [{r.score:.3f}] {r.title}  ({r.source})")
        print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
