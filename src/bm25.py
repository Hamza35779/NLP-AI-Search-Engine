"""Okapi BM25 ranking on top of an `InvertedIndex`.

The score for a (query, document) pair is:

    BM25(q, d) = Σ_t∈q   IDF(t) * (tf(t, d) * (k1 + 1)) /
                         (tf(t, d) + k1 * (1 - b + b * |d| / avgdl))

with the smoothed IDF

    IDF(t) = log( (N - df(t) + 0.5) / (df(t) + 0.5) + 1 )

`k1` controls term-frequency saturation (default 1.5) and `b` controls
length normalization (default 0.75).
"""

from __future__ import annotations

import math
from typing import Dict, Iterable, List, Optional, Tuple

from .config import DEFAULT_CONFIG, EngineConfig
from .indexer import InvertedIndex


class BM25Model:
    """Standalone BM25 scorer keyed off an `InvertedIndex`."""

    def __init__(
        self,
        index: InvertedIndex,
        config: Optional[EngineConfig] = None,
    ) -> None:
        self.index = index
        cfg = config or DEFAULT_CONFIG
        self.k1: float = cfg.bm25_k1
        self.b: float = cfg.bm25_b

        self._idf: Dict[str, float] = {}
        self._fit()

    # ------------------------------------------------------------------ build
    def _fit(self) -> None:
        n = self.index.num_documents
        for term in self.index.vocabulary:
            df = self.index.doc_frequency(term)
            # Robertson-Spärck Jones IDF, +1 keeps the value strictly positive.
            self._idf[term] = math.log(((n - df + 0.5) / (df + 0.5)) + 1.0)

    # ------------------------------------------------------------------ query
    def score(self, query_terms: Iterable[str]) -> List[Tuple[int, float]]:
        avgdl = self.index.avg_doc_length or 1.0

        # Aggregate per-document scores across all query terms.
        scores: Dict[int, float] = {}
        for term in query_terms:
            postings = self.index.postings(term)
            if not postings:
                continue
            idf = self._idf.get(term, 0.0)
            if idf <= 0:
                continue
            for doc_id, tf, _positions in postings:
                dl = self.index.doc_length(doc_id) or 1
                norm = 1.0 - self.b + self.b * (dl / avgdl)
                denom = tf + self.k1 * norm
                contrib = idf * (tf * (self.k1 + 1.0)) / denom
                scores[doc_id] = scores.get(doc_id, 0.0) + contrib

        ranked = [(doc_id, score) for doc_id, score in scores.items() if score > 0]
        ranked.sort(key=lambda x: x[1], reverse=True)
        return ranked

    # --------------------------------------------------------------- helpers
    def idf(self, term: str) -> float:
        return self._idf.get(term, 0.0)

    def explain(self, term: str, doc_id: int) -> Dict[str, float]:
        """Return the BM25 components for a single (term, document) pair."""
        avgdl = self.index.avg_doc_length or 1.0
        tf = self.index.term_frequency(term, doc_id)
        dl = self.index.doc_length(doc_id) or 1
        idf = self._idf.get(term, 0.0)
        norm = 1.0 - self.b + self.b * (dl / avgdl)
        denom = tf + self.k1 * norm if tf else 1.0
        contribution = idf * (tf * (self.k1 + 1.0)) / denom if tf else 0.0
        return {
            "tf": float(tf),
            "doc_length": float(dl),
            "avgdl": float(avgdl),
            "idf": float(idf),
            "k1": self.k1,
            "b": self.b,
            "score": float(contribution),
        }
