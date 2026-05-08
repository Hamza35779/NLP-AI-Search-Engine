"""Glue between the inverted index and the available ranking models.

The `Ranker` exposes a single ``rank(query_tokens)`` method that the
`SearchEngine` uses regardless of which scoring model the user picked.
"""

from __future__ import annotations

from typing import Iterable, List, Tuple

from .bm25 import BM25Model
from .indexer import InvertedIndex
from .tfidf import TfIdfModel


VALID_MODELS = ("bm25", "tfidf")


class Ranker:
    """Lazy wrapper around the two ranking models."""

    def __init__(self, index: InvertedIndex, model: str = "bm25") -> None:
        if model not in VALID_MODELS:
            raise ValueError(
                f"Unknown ranking model {model!r}. Choose one of {VALID_MODELS}."
            )
        self.index = index
        self.model_name = model
        self._tfidf: TfIdfModel | None = None
        self._bm25: BM25Model | None = None

    # ------------------------------------------------------------- lazy fits
    @property
    def tfidf(self) -> TfIdfModel:
        if self._tfidf is None:
            self._tfidf = TfIdfModel(self.index)
        return self._tfidf

    @property
    def bm25(self) -> BM25Model:
        if self._bm25 is None:
            self._bm25 = BM25Model(self.index)
        return self._bm25

    # --------------------------------------------------------------- public
    def rank(self, query_tokens: Iterable[str]) -> List[Tuple[int, float]]:
        tokens = list(query_tokens)
        if self.model_name == "bm25":
            return self.bm25.score(tokens)
        return self.tfidf.score(tokens)

    def use_model(self, model: str) -> None:
        if model not in VALID_MODELS:
            raise ValueError(
                f"Unknown ranking model {model!r}. Choose one of {VALID_MODELS}."
            )
        self.model_name = model

    def explain(self, query_tokens: Iterable[str], doc_id: int) -> List[dict]:
        """Show which terms contributed to the score (BM25 only)."""
        if self.model_name != "bm25":
            raise ValueError("explain() is only implemented for BM25.")
        breakdown: List[dict] = []
        total = 0.0
        for term in query_tokens:
            row = self.bm25.explain(term, doc_id)
            row["term"] = term
            total += row["score"]
            breakdown.append(row)
        breakdown.append({"term": "__total__", "score": total})
        return breakdown
