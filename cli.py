"""Command-line interface for the NLP search engine.

Examples
--------

Build the index from the bundled corpus and run a one-off query::

    python cli.py "machine learning"

Use a different ranking model::

    python cli.py --model tfidf "neural networks"

Point at a different corpus directory::

    python cli.py --corpus path/to/docs "your query"
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import List

from src.config import EngineConfig
from src.search_engine import SearchEngine, SearchResult


def _build_engine(corpus: str, model: str) -> SearchEngine:
    cfg = EngineConfig()
    engine = SearchEngine(cfg, model=model)
    if not os.path.exists(corpus):
        print(f"[!] Corpus not found at {corpus}", file=sys.stderr)
        sys.exit(2)
    engine.index_corpus(corpus)
    return engine


def _print_results(query: str, results: List[SearchResult], as_json: bool) -> None:
    if as_json:
        print(
            json.dumps(
                {"query": query, "results": [r.to_dict() for r in results]},
                indent=2,
            )
        )
        return

    if not results:
        print("No matching documents.")
        return

    print(f"Top {len(results)} results for: {query}\n")
    for rank, r in enumerate(results, start=1):
        score = f"{r.score:.4f}"
        print(f"{rank:>2}. [{score}] {r.title}")
        if r.source:
            print(f"     source: {r.source}")
        # Strip the highlight markers in plain output; the CLI is text-only.
        plain = (
            r.snippet.replace("<mark>", "").replace("</mark>", "").strip()
        )
        if plain:
            print(f"     {plain}")
        print()


def _interactive(engine: SearchEngine, top_k: int, as_json: bool) -> int:
    print(f"Index ready: {engine.stats()}")
    print('Type a query (Ctrl-C or empty line to exit).')
    while True:
        try:
            raw = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return 0
        if not raw:
            return 0
        results = engine.search(raw, top_k=top_k)
        if not results:
            suggestion = engine.suggest_query(raw)
            if suggestion:
                print(f"Did you mean: {suggestion}?")
                results = engine.search(suggestion, top_k=top_k)
        _print_results(raw, results, as_json)


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the NLP search engine.")
    parser.add_argument("query", nargs="*", help="Query string. Omit to enter REPL mode.")
    parser.add_argument(
        "--corpus",
        default=os.path.join("data", "sample_docs"),
        help="Path to the corpus directory or JSON file.",
    )
    parser.add_argument(
        "--model",
        choices=("bm25", "tfidf"),
        default="bm25",
        help="Ranking model to use.",
    )
    parser.add_argument(
        "--top-k", type=int, default=5, help="Number of results to print."
    )
    parser.add_argument(
        "--json", action="store_true", help="Emit JSON instead of plain text."
    )
    args = parser.parse_args(argv)

    engine = _build_engine(args.corpus, args.model)

    if not args.query:
        return _interactive(engine, args.top_k, args.json)

    query = " ".join(args.query)
    results = engine.search(query, top_k=args.top_k)
    if not results:
        suggestion = engine.suggest_query(query)
        if suggestion and suggestion != query:
            print(f"No exact matches. Did you mean: {suggestion}?")
            results = engine.search(suggestion, top_k=args.top_k)
            query = suggestion
    _print_results(query, results, args.json)
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
