"""Semantic search using TF-IDF vectors as lightweight embeddings."""

from __future__ import annotations

import math
from typing import Dict, List, Optional

from .document import Document
from .preprocessing import Preprocessor


class SemanticSearch:
    """Lightweight semantic search using TF-IDF vectors."""

    def __init__(self, indexer, preprocessor: Preprocessor, doc_lookup: Dict[int, Document]) -> None:
        self.indexer = indexer
        self.preprocessor = preprocessor
        self.doc_lookup = doc_lookup
        self._vocab_list: List[str] = []
        self._vocab_index: Dict[str, int] = {}
        self._doc_vectors: Dict[int, List[float]] = {}
        self._build_vectors()

    def _build_vectors(self) -> None:
        """Build TF-IDF vectors for all documents."""
        vocab = self.indexer.vocabulary
        self._vocab_list = list(vocab)
        self._vocab_index = {term: idx for idx, term in enumerate(self._vocab_list)}
        vocab_size = len(self._vocab_list)
        n = self.indexer.num_documents

        for doc_id, doc in self.doc_lookup.items():
            vector = [0.0] * vocab_size
            tokens = self.preprocessor.process(doc.text)
            term_counts: Dict[str, int] = {}
            for term in tokens:
                term_counts[term] = term_counts.get(term, 0) + 1

            for term, count in term_counts.items():
                if term in self._vocab_index:
                    idx = self._vocab_index[term]
                    tf = 1 + math.log(count) if count > 0 else 0
                    df = self.indexer.doc_frequency(term)
                    idf = math.log((n + 1) / (df + 1)) + 1
                    vector[idx] = tf * idf

            norm = math.sqrt(sum(v * v for v in vector))
            if norm > 0:
                vector = [v / norm for v in vector]
            self._doc_vectors[doc_id] = vector

    def search(self, query: str, top_k: int = 10) -> List[SearchResult]:
        """Search using cosine similarity of TF-IDF vectors."""
        tokens = self.preprocessor.process(query)
        vocab_size = len(self._vocab_list)
        n = self.indexer.num_documents

        query_vector = [0.0] * vocab_size
        term_counts: Dict[str, int] = {}
        for term in tokens:
            term_counts[term] = term_counts.get(term, 0) + 1

        for term, count in term_counts.items():
            if term in self._vocab_index:
                idx = self._vocab_index[term]
                tf = 1 + math.log(count) if count > 0 else 0
                df = self.indexer.doc_frequency(term)
                idf = math.log((n + 1) / (df + 1)) + 1
                query_vector[idx] = tf * idf

        results = []
        from .search_engine import SearchResult
        for doc_id, doc_vector in self._doc_vectors.items():
            score = sum(q * d for q, d in zip(query_vector, doc_vector))
            if score > 0:
                doc = self.doc_lookup[doc_id]
                snippet = self._generate_snippet(doc.text, tokens)
                results.append(SearchResult(
                    doc_id=doc_id,
                    title=doc.title,
                    snippet=snippet,
                    score=score,
                    source=doc.source,
                    url=doc.url,
                    domain=doc.domain,
                ))

        results.sort(key=lambda x: x.score, reverse=True)
        return results[:top_k]

    def _generate_snippet(self, content: str, query_terms: List[str], window: int = 12) -> str:
        """Generate snippet with highlighted terms."""
        words = content.split()
        query_terms_set = set(term.lower() for term in query_terms)

        best_start = 0
        best_score = 0
        for i in range(max(1, len(words) - window + 1)):
            score = sum(1 for w in words[i:i+window] if w.lower() in query_terms_set)
            if score > best_score:
                best_score = score
                best_start = i

        snippet_words = words[best_start:best_start + window]
        snippet = " ".join(snippet_words)
        if best_start > 0:
            snippet = "..." + snippet
        if best_start + window < len(words):
            snippet = snippet + "..."

        for term in query_terms:
            snippet = snippet.replace(term, f"<mark>{term}</mark>")
            snippet = snippet.replace(term.capitalize(), f"<mark>{term.capitalize()}</mark>")

        return snippet
