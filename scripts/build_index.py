"""Build (or rebuild) the search index from a corpus and persist it to disk.

Usage::

    python scripts/build_index.py [--corpus DIR] [--out PATH]
"""

from __future__ import annotations

import argparse
import os
import sys

# Allow running as `python scripts/build_index.py` from the repo root.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)))

from src.config import EngineConfig  # noqa: E402  (path tweak above)
from src.search_engine import SearchEngine  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the search index.")
    parser.add_argument(
        "--corpus",
        default=os.path.join("data", "sample_docs"),
        help="Directory of text/markdown files or a JSON corpus file.",
    )
    parser.add_argument(
        "--out",
        default=None,
        help="Where to write the pickled index (defaults to EngineConfig.index_path).",
    )
    parser.add_argument(
        "--model",
        choices=("bm25", "tfidf"),
        default="bm25",
        help="Default ranking model to bake into the saved engine.",
    )
    args = parser.parse_args()

    cfg = EngineConfig()
    if args.out:
        cfg.index_path = args.out

    if not os.path.exists(args.corpus):
        print(f"[!] Corpus path does not exist: {args.corpus}", file=sys.stderr)
        return 2

    engine = SearchEngine(cfg, model=args.model)
    engine.index_corpus(args.corpus)
    saved_to = engine.save()
    print(f"Indexed {engine.index.num_documents} documents -> {saved_to}")
    print(f"Stats: {engine.stats()}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
