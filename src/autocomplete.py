"""Query autocomplete suggestions."""

from __future__ import annotations

import re
from typing import List, Optional, Set


class Autocomplete:
    """Provide autocomplete suggestions based on vocabulary and query history."""

    def __init__(
        self,
        vocabulary: List[str],
        query_history: List[str],
        max_suggestions: int = 10,
    ) -> None:
        self.vocabulary: Set[str] = set(vocabulary)
        self.query_history: List[str] = query_history
        self.max_suggestions = max_suggestions

    def suggest(self, prefix: str, limit: int = 5) -> List[str]:
        """Suggest completions for the given prefix."""
        if not prefix:
            return []

        prefix_lower = prefix.lower()
        suggestions: List[str] = []

        # First, check query history for prefix matches
        seen: Set[str] = set()
        for query in reversed(self.query_history):
            if query.lower().startswith(prefix_lower) and query not in seen:
                suggestions.append(query)
                seen.add(query)
                if len(suggestions) >= limit:
                    return suggestions

        # Then check vocabulary for prefix matches
        for term in sorted(self.vocabulary):
            if term.startswith(prefix_lower) and term not in seen:
                suggestions.append(term)
                seen.add(term)
                if len(suggestions) >= limit:
                    return suggestions

        return suggestions[:limit]

    def suggest_next_term(self, partial_query: str, limit: int = 5) -> List[str]:
        """Suggest next term based on partial query."""
        if not partial_query:
            return self._get_popular_queries(limit)

        tokens = partial_query.lower().split()
        if not tokens:
            return self._get_popular_queries(limit)

        last_token = tokens[-1]
        suggestions = self.suggest(last_token, limit)

        # If last token is complete, suggest next possible terms
        if last_token in suggestions or not suggestions:
            suggestions = self._suggest_following_terms(tokens, limit)

        return suggestions[:limit]

    def _get_popular_queries(self, limit: int) -> List[str]:
        """Get popular queries."""
        query_counts: dict = {}
        for query in self.query_history:
            query_counts[query] = query_counts.get(query, 0) + 1
        sorted_queries = sorted(query_counts.items(), key=lambda x: x[1], reverse=True)
        return [q for q, _ in sorted_queries[:limit]]

    def _suggest_following_terms(self, tokens: List[str], limit: int) -> List[str]:
        """Suggest terms that frequently follow the given tokens."""
        if not tokens:
            return []

        query_text = " ".join(tokens)
        following: dict = {}
        for query in self.query_history:
            if query.startswith(query_text) and len(query) > len(query_text):
                next_term = query[len(query_text):].strip().split()[0]
                following[next_term] = following.get(next_term, 0) + 1

        sorted_terms = sorted(following.items(), key=lambda x: x[1], reverse=True)
        return [term for term, _ in sorted_terms[:limit]]

    def update_vocabulary(self, new_terms: List[str]) -> None:
        """Update vocabulary with new terms."""
        self.vocabulary.update(new_terms)

    def add_query(self, query: str) -> None:
        """Add a query to history."""
        self.query_history.append(query)
        # Keep history manageable
        if len(self.query_history) > 10000:
            self.query_history = self.query_history[-5000:]
