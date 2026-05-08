"""NLP search engine package.

Exposes the high-level `SearchEngine` facade so callers can simply do
``from src import SearchEngine``.
"""

from .analytics import SearchAnalytics
from .autocomplete import Autocomplete
from .search_engine import SearchEngine
from .semantic_search import SemanticSearch

__all__ = ["SearchEngine", "SemanticSearch", "SearchAnalytics", "Autocomplete"]
__version__ = "0.3.0"
