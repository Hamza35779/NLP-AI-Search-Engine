"""Tunable parameters used across the search engine."""

from dataclasses import dataclass, field
from typing import Set


DEFAULT_STOPWORDS: Set[str] = {
    "a", "an", "and", "are", "as", "at", "be", "but", "by", "for", "from",
    "has", "have", "he", "her", "his", "i", "if", "in", "into", "is", "it",
    "its", "no", "not", "of", "on", "or", "she", "so", "such", "than", "that",
    "the", "their", "then", "there", "these", "they", "this", "to", "was",
    "were", "will", "with", "you", "your", "we", "our", "us", "do", "does",
    "did", "been", "being", "having", "had", "would", "could", "should",
    "may", "might", "must", "shall", "can", "about", "above", "after",
    "again", "against", "all", "am", "any", "because", "before", "below",
    "between", "both", "down", "during", "each", "few", "further", "here",
    "how", "i'm", "more", "most", "off", "once", "only", "other", "out",
    "over", "own", "same", "some", "through", "too", "under", "until", "up",
    "very", "what", "when", "where", "which", "while", "who", "whom", "why",
}


@dataclass
class EngineConfig:
    """Knobs for the index, ranker, and snippet generator."""

    use_stemming: bool = True
    remove_stopwords: bool = True
    min_token_length: int = 2

    # BM25
    bm25_k1: float = 1.5
    bm25_b: float = 0.75

    # Snippet generator
    snippet_window: int = 12
    max_snippets: int = 1

    # Spell-correction
    spell_max_distance: int = 2
    spell_top_k: int = 3

    # Index serialization
    index_path: str = "index_data/engine.pkl"

    # Analytics
    enable_analytics: bool = True
    analytics_path: str = "index_data/analytics.json"

    # Autocomplete
    enable_autocomplete: bool = True

    # Semantic search
    enable_semantic: bool = True

    stopwords: Set[str] = field(default_factory=lambda: set(DEFAULT_STOPWORDS))


DEFAULT_CONFIG = EngineConfig()
