"""High-level search facade tying every component together."""

from __future__ import annotations

import os
import time
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional

from .analytics import SearchAnalytics
from .autocomplete import Autocomplete
from .cache import search_cache
from .config import DEFAULT_CONFIG, EngineConfig
from .document import Document
from .document_loader import iter_documents
from .indexer import InvertedIndex
from .preprocessing import Preprocessor
from .query_processor import ParsedQuery, QueryProcessor
from .ranker import Ranker
from .semantic_search import SemanticSearch
from .snippet import SnippetGenerator
from .spell_check import SpellCorrector
from .utils import load_pickle, save_pickle


@dataclass
class SearchResult:
    doc_id: int
    title: str
    snippet: str
    score: float
    source: Optional[str]
    url: Optional[str] = None
    domain: str = ""

    def to_dict(self) -> dict:
        return {
            "doc_id": self.doc_id,
            "title": self.title,
            "snippet": self.snippet,
            "score": round(float(self.score), 5),
            "source": self.source,
            "url": self.url,
            "domain": self.domain,
        }


class SearchEngine:
    """Configure once, query many times."""

    def __init__(
        self,
        config: Optional[EngineConfig] = None,
        model: str = "bm25",
    ) -> None:
        self.config = config or DEFAULT_CONFIG
        self.preprocessor = Preprocessor(self.config)
        self.index = InvertedIndex(self.config, self.preprocessor)
        self.ranker = Ranker(self.index, model=model)
        self.query_processor = QueryProcessor(self.preprocessor, self.config)
        self.snippet = SnippetGenerator(
            self.preprocessor,
            window=self.config.snippet_window,
            max_snippets=self.config.max_snippets,
        )
        self._speller: Optional[SpellCorrector] = None
        self._page_rank_scores: dict = {}
        self._enable_cache = True

        # New features
        self._analytics: Optional[SearchAnalytics] = None
        self._autocomplete: Optional[Autocomplete] = None
        self._semantic_search: Optional[SemanticSearch] = None

        if self.config.enable_analytics:
            self._init_analytics()

        if self.config.enable_autocomplete:
            self._init_autocomplete()

        if self.config.enable_semantic:
            self._init_semantic_search()

    def _init_analytics(self) -> None:
        """Initialize analytics tracking."""
        self._analytics = SearchAnalytics()
        if self.config.analytics_path and os.path.exists(self.config.analytics_path):
            self._analytics.load(self.config.analytics_path)

    def _init_autocomplete(self) -> None:
        """Initialize autocomplete."""
        self._autocomplete = Autocomplete(
            vocabulary=self.index.vocabulary if self.index else [],
            query_history=[],
        )

    def _init_semantic_search(self) -> None:
        """Initialize semantic search."""
        if self.index and self.index.num_documents > 0:
            doc_lookup = {doc.doc_id: doc for doc in self.index.all_documents()}
            self._semantic_search = SemanticSearch(self.index, self.preprocessor, doc_lookup)

    def enable_cache(self, enabled: bool = True):
        """Toggle caching on/off."""
        self._enable_cache = enabled

    # ------------------------------------------------------------------ build
    def index_documents(self, docs: Iterable[Document]) -> "SearchEngine":
        self.index.build(docs)
        # Invalidate cached helpers so they refit on next use.
        self.ranker = Ranker(self.index, model=self.ranker.model_name)
        self._speller = None
        self._page_rank_scores = {}
        # Update autocomplete vocabulary
        if self._autocomplete:
            for doc in self.index.all_documents():
                tokens = self.preprocessor.process(doc.text)
                self._autocomplete.update_vocabulary(tokens)
        # Reinitialize semantic search
        if self.config.enable_semantic:
            self._init_semantic_search()
        return self

    def index_corpus(self, path: str) -> "SearchEngine":
        return self.index_documents(iter_documents(path))

    def compute_page_rank(self, damping: float = 0.85, max_iter: int = 100, tol: float = 1e-6):
        """Compute PageRank-like scores based on inbound_links."""
        docs = self.index._documents
        n = len(docs)
        if n == 0:
            return
        
        # Initialize scores
        scores = {doc.doc_id: 1.0 / n for doc in docs}
        
        for _ in range(max_iter):
            new_scores = {}
            for doc in docs:
                # Base score from damping
                score = (1 - damping) / n
                # Add contributions from documents linking to this one
                # Simplified: use inbound_links count
                if doc.inbound_links > 0:
                    score += damping * (doc.inbound_links / max(1, sum(d.inbound_links for d in docs))) * sum(scores.values())
                new_scores[doc.doc_id] = score
            
            # Check convergence
            diff = sum(abs(new_scores[d] - scores[d]) for d in scores)
            scores = new_scores
            if diff < tol:
                break
        
        self._page_rank_scores = scores

    def get_authority_score(self, doc_id: int) -> float:
        """Get the authority score (PageRank-like) for a document."""
        if not self._page_rank_scores:
            self.compute_page_rank()
        return self._page_rank_scores.get(doc_id, 0.1)

    # ------------------------------------------------------------------ query
    def parse(self, raw_query: str) -> ParsedQuery:
        return self.query_processor.parse(raw_query)

    def search(self, raw_query: str, top_k: int = 10) -> List[SearchResult]:
        start_time = time.time()

        # Check cache
        if self._enable_cache and raw_query:
            cached = search_cache.get(raw_query, self.ranker.model_name, top_k)
            if cached:
                return [SearchResult(**r) for r in cached]

        parsed = self.parse(raw_query)
        if parsed.is_empty():
            return []

        ranked = self.ranker.rank(parsed.all_positive_terms)
        if not ranked:
            return []

        # Phrase / boolean filters
        ranked = self._apply_phrase_filter(ranked, parsed.phrases)
        ranked = self._apply_must_filter(ranked, parsed.must_terms, parsed.operator)
        ranked = self._apply_must_not_filter(ranked, parsed.must_not_terms)

        # Apply authority boosting (PageRank-like)
        if self._page_rank_scores:
            ranked = [(doc_id, score * (1 + 0.5 * self._page_rank_scores.get(doc_id, 0)))
                      for doc_id, score in ranked]
            ranked.sort(key=lambda x: x[1], reverse=True)

        results: List[SearchResult] = []
        for doc_id, score in ranked[:top_k]:
            doc = self.index.document(doc_id)
            snippet = self.snippet.generate(doc.text, parsed.all_positive_terms)
            results.append(
                SearchResult(
                    doc_id=doc_id,
                    title=doc.title,
                    snippet=snippet,
                    score=score,
                    source=doc.source,
                    url=doc.url or doc.source,
                    domain=doc.domain,
                )
            )

        # Cache results
        if self._enable_cache and raw_query:
            search_cache.set(raw_query, self.ranker.model_name, top_k, [r.to_dict() for r in results])

        # Track analytics
        if self._analytics:
            response_time = time.time() - start_time
            self._analytics.record_query(raw_query, self.ranker.model_name, len(results), response_time)

        return results

    def semantic_search(self, query: str, top_k: int = 10) -> List[SearchResult]:
        """Perform semantic search using TF-IDF vectors."""
        if not self._semantic_search:
            if self.config.enable_semantic:
                self._init_semantic_search()
            if not self._semantic_search:
                return []
        return self._semantic_search.search(query, top_k)

    def get_autocomplete_suggestions(self, prefix: str, limit: int = 5) -> List[str]:
        """Get autocomplete suggestions."""
        if not self._autocomplete:
            return []
        return self._autocomplete.suggest_next_term(prefix, limit)

    def get_analytics(self) -> dict:
        """Get search analytics."""
        if not self._analytics:
            return {"error": "Analytics not enabled"}
        return self._analytics.get_stats()

    def get_top_queries(self, limit: int = 10) -> List[dict]:
        """Get top queries."""
        if not self._analytics:
            return []
        return self._analytics.get_top_queries(limit)

    def get_related_queries(self, query: str, limit: int = 5) -> List[str]:
        """Get related queries."""
        if self._analytics:
            return self._analytics.get_related_queries(query, limit)
        return []

    def add_document(self, doc: Document) -> None:
        """Add a document to the index."""
        self.index.add_document(doc)
        # Reinitialize components that depend on the index
        self.ranker = Ranker(self.index, model=self.ranker.model_name)
        self._speller = None
        self._page_rank_scores = {}
        # Reinitialize semantic search if enabled
        if self.config.enable_semantic:
            self._init_semantic_search()
        # Update autocomplete vocabulary
        if self._autocomplete:
            tokens = self.preprocessor.process(doc.text)
            self._autocomplete.update_vocabulary(tokens)

    def remove_document(self, doc_id: int) -> bool:
        """Remove a document from the index."""
        if doc_id not in self.index._documents:
            return False
        # Remove from index structures
        doc = self.index._documents[doc_id]
        del self.index._documents[doc_id]
        del self.index._doc_lengths[doc_id]
        # Remove from postings
        for term, postings in self.index._postings.items():
            self.index._postings[term] = [p for p in postings if p[0] != doc_id]
        # Reinitialize components
        self.ranker = Ranker(self.index, model=self.ranker.model_name)
        self._speller = None
        self._page_rank_scores = {}
        if self.config.enable_semantic:
            self._init_semantic_search()
        return True

    # ----- filters ---------------------------------------------------------
    def _apply_phrase_filter(self, ranked, phrases):
        if not phrases:
            return ranked
        kept = []
        for doc_id, score in ranked:
            if all(self._doc_contains_phrase(doc_id, phrase) for phrase in phrases):
                kept.append((doc_id, score))
        return kept

    def _apply_must_filter(self, ranked, must_terms, operator):
        if not must_terms and operator != "AND":
            return ranked
        terms = list(must_terms)
        kept = []
        for doc_id, score in ranked:
            if all(self.index.term_frequency(t, doc_id) > 0 for t in terms):
                kept.append((doc_id, score))
        return kept

    def _apply_must_not_filter(self, ranked, must_not_terms):
        if not must_not_terms:
            return ranked
        kept = []
        for doc_id, score in ranked:
            if not any(self.index.term_frequency(t, doc_id) > 0 for t in must_not_terms):
                kept.append((doc_id, score))
        return kept

    def _doc_contains_phrase(self, doc_id: int, phrase: List[str]) -> bool:
        if not phrase:
            return True
        first_positions = self.index.positions(phrase[0], doc_id)
        if not first_positions:
            return False
        for start in first_positions:
            if all(
                (start + offset) in self.index.positions(term, doc_id)
                for offset, term in enumerate(phrase)
            ):
                return True
        return False

    # ----- spell-correction -----------------------------------------------
    def speller(self) -> SpellCorrector:
        if self._speller is None:
            self._speller = SpellCorrector(
                self.index.vocabulary,
                max_distance=self.config.spell_max_distance,
                top_k=self.config.spell_top_k,
            )
        return self._speller

    def suggest_query(self, raw_query: str) -> Optional[str]:
        speller = self.speller()
        tokens = self.preprocessor.tokenize(raw_query)
        if not tokens:
            return None
        suggestions = []
        changed = False
        for tok in tokens:
            stem = self.preprocessor.normalize([tok])
            if stem and stem[0] in self.index.vocabulary:
                suggestions.append(tok)
                continue
            best = speller.best(stem[0]) if stem else None
            if best:
                suggestions.append(best)
                changed = True
            else:
                suggestions.append(tok)
        return " ".join(suggestions) if changed else None

    # ----- persistence -----------------------------------------------------
    def save(self, path: Optional[str] = None) -> str:
        target = path or self.config.index_path
        save_pickle(self, target)
        # Save analytics if enabled
        if self._analytics and self.config.analytics_path:
            self._analytics.save(self.config.analytics_path)
        return target

    @classmethod
    def load(cls, path: str) -> "SearchEngine":
        loaded = load_pickle(path)
        if not isinstance(loaded, cls):
            raise TypeError(f"File {path} did not contain a SearchEngine instance")
        # Initialize analytics after load
        if loaded.config.enable_analytics:
            loaded._init_analytics()
        if loaded.config.enable_autocomplete:
            loaded._init_autocomplete()
        if loaded.config.enable_semantic:
            loaded._init_semantic_search()
        return loaded

    # ----- diagnostics -----------------------------------------------------
    def stats(self) -> dict:
        info = self.index.stats()
        info["model"] = self.ranker.model_name
        return info
