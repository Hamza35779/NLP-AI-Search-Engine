"""Tiny spell-checker that suggests near-matches against the index vocabulary.

Uses Damerau-Levenshtein edit distance so transpositions (``teh`` -> ``the``)
cost 1 edit instead of 2. The vocabulary is fixed at construction time.
"""

from __future__ import annotations

from typing import Iterable, List, Optional, Tuple


def damerau_levenshtein(a: str, b: str, max_distance: Optional[int] = None) -> int:
    """Edit distance with transpositions allowed.

    If `max_distance` is provided we early-exit once the running minimum on
    a row exceeds it, returning ``max_distance + 1`` — fast enough for
    interactive use even on a large vocabulary.
    """
    la, lb = len(a), len(b)
    if abs(la - lb) > (max_distance or max(la, lb)):
        return (max_distance or max(la, lb)) + 1

    # Two-row DP plus the row from two iterations ago for transpositions.
    prev_prev: List[int] = []
    prev: List[int] = list(range(lb + 1))
    for i in range(1, la + 1):
        curr = [i] + [0] * lb
        row_min = curr[0]
        for j in range(1, lb + 1):
            cost = 0 if a[i - 1] == b[j - 1] else 1
            curr[j] = min(
                curr[j - 1] + 1,         # insertion
                prev[j] + 1,             # deletion
                prev[j - 1] + cost,      # substitution
            )
            if (
                i > 1 and j > 1
                and a[i - 1] == b[j - 2]
                and a[i - 2] == b[j - 1]
            ):
                curr[j] = min(curr[j], prev_prev[j - 2] + 1)
            if curr[j] < row_min:
                row_min = curr[j]
        if max_distance is not None and row_min > max_distance:
            return max_distance + 1
        prev_prev = prev
        prev = curr
    return prev[lb]


class SpellCorrector:
    """Suggests vocabulary terms close to a misspelled query token."""

    def __init__(
        self,
        vocabulary: Iterable[str],
        max_distance: int = 2,
        top_k: int = 3,
    ) -> None:
        self._vocab = sorted(set(vocabulary))
        self.max_distance = max_distance
        self.top_k = top_k

    def suggest(self, term: str) -> List[Tuple[str, int]]:
        """Top suggestions for `term` as ``(candidate, distance)`` tuples."""
        if not term or term in self._vocab:
            return []
        scored: List[Tuple[str, int]] = []
        for word in self._vocab:
            d = damerau_levenshtein(term, word, self.max_distance)
            if d <= self.max_distance:
                scored.append((word, d))
        scored.sort(key=lambda x: (x[1], x[0]))
        return scored[: self.top_k]

    def best(self, term: str) -> Optional[str]:
        suggestions = self.suggest(term)
        return suggestions[0][0] if suggestions else None
