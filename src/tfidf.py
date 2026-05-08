"""TF-IDF model on top of an `InvertedIndex`.

We use the standard log-tf weighting with smoothed IDF:

    tf_weight(t, d) = 1 + log(tf(t, d))           if tf(t, d) > 0
    idf(t)          = log(N / df(t))              with N = total documents
    weight(t, d)    = tf_weight(t, d) * idf(t)

Document and query vectors are then compared with cosine similarity from
`utils.cosine`.
"""

from __future__ import annotations

import math
from typing import Dict, Iterable, List, Tuple

from .indexer import InvertedIndex
from .utils import cosine, safe_log


class TfIdfModel:
    """Sparse TF-IDF representation over an inverted index."""

    def __init__(self, index: InvertedIndex) -> None:
        self.index = index
        self._idf: Dict[str, float] = {}
        self._doc_vectors: Dict[int, Dict[str, float]] = {}
        self._fit()

    # ------------------------------------------------------------------ build
    def _fit(self) -> None:
        n = max(self.index.num_documents, 1)
        for term in self.index.vocabulary:
            df = self.index.doc_frequency(term)
            # Smoothed IDF: avoid log(0) when df==N.
            self._idf[term] = safe_log((n + 1) / (df + 1)) + 1.0

        for doc in self.index.all_documents():
            self._doc_vectors[doc.doc_id] = self._vector_for_doc(doc.doc_id)

    def _vector_for_doc(self, doc_id: int) -> Dict[str, float]:
        vec: Dict[str, float] = {}
        for term in self.index.vocabulary:
            tf = self.index.term_frequency(term, doc_id)
            if tf == 0:
                continue
            tf_weight = 1.0 + math.log(tf)
            vec[term] = tf_weight * self._idf.get(term, 0.0)
        return vec

    # ------------------------------------------------------------------ query
    def vectorize_query(self, terms: Iterable[str]) -> Dict[str, float]:
        counts: Dict[str, int] = {}
        for term in terms:
            counts[term] = counts.get(term, 0) + 1
        vec: Dict[str, float] = {}
        for term, tf in counts.items():
            idf = self._idf.get(term)
            if idf is None or idf == 0.0:
                continue
            tf_weight = 1.0 + math.log(tf)
            vec[term] = tf_weight * idf
        return vec

    def score(self, query_terms: Iterable[str]) -> List[Tuple[int, float]]:
        """Return ``[(doc_id, score), ...]`` sorted by descending score."""
        q_vec = self.vectorize_query(query_terms)
        if not q_vec:
            return []

        # Restrict to docs that share at least one query term.
        candidates: set[int] = set()
        for term in q_vec:
            candidates.update(self.index.documents_containing(term))

        scored: List[Tuple[int, float]] = []
        for doc_id in candidates:
            d_vec = self._doc_vectors.get(doc_id)
            if not d_vec:
                continue
            sim = cosine(q_vec, d_vec)
            if sim > 0:
                scored.append((doc_id, sim))
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored

    # --------------------------------------------------------------- helpers
    def idf(self, term: str) -> float:
        return self._idf.get(term, 0.0)

    def doc_vector(self, doc_id: int) -> Dict[str, float]:
        return dict(self._doc_vectors.get(doc_id, {}))
