"""Generate result snippets with the matched query terms highlighted.

The snippet generator works on the *original* document text (so casing and
punctuation are preserved). It picks the best window in the document — the
one containing the most distinct query terms — and wraps each match in
``<mark>`` tags by default.
"""

from __future__ import annotations

import re
from typing import Iterable, List, Optional, Tuple

from .preprocessing import Preprocessor


_WORD_RE = re.compile(r"\w+|\W+", re.UNICODE)


def _split_with_offsets(text: str) -> List[Tuple[str, int]]:
    """Tokenize keeping byte offsets so we can stitch a snippet back."""
    out: List[Tuple[str, int]] = []
    i = 0
    for match in _WORD_RE.finditer(text):
        token = match.group(0)
        out.append((token, i))
        i += len(token)
    return out


class SnippetGenerator:
    """Picks the most relevant window from a document and highlights it."""

    def __init__(
        self,
        preprocessor: Preprocessor,
        window: int = 12,
        max_snippets: int = 1,
        highlight_open: str = "<mark>",
        highlight_close: str = "</mark>",
    ) -> None:
        self.preprocessor = preprocessor
        self.window = max(window, 4)
        self.max_snippets = max_snippets
        self.highlight_open = highlight_open
        self.highlight_close = highlight_close

    # ------------------------------------------------------------------
    def _is_match(self, raw_token: str, query_stems: Iterable[str]) -> bool:
        if not raw_token.strip() or not raw_token[0].isalpha():
            return False
        processed = self.preprocessor.process(raw_token)
        if not processed:
            return False
        stems = set(query_stems)
        return any(p in stems for p in processed)

    def _best_window(
        self,
        tokens: List[Tuple[str, int]],
        query_stems: List[str],
    ) -> Tuple[int, int]:
        # We score windows by the count of distinct query terms they contain.
        if not tokens:
            return (0, 0)
        match_flags = [self._is_match(tok, query_stems) for tok, _ in tokens]

        best_start, best_score = 0, -1
        for start in range(len(tokens)):
            end = min(start + self.window, len(tokens))
            score = sum(1 for k in range(start, end) if match_flags[k])
            if score > best_score:
                best_start, best_score = start, score
            if end == len(tokens):
                break
        return (best_start, min(best_start + self.window, len(tokens)))

    def _render(
        self,
        tokens: List[Tuple[str, int]],
        start: int,
        end: int,
        query_stems: List[str],
    ) -> str:
        if start >= end:
            return ""
        parts: List[str] = []
        for tok, _offset in tokens[start:end]:
            if self._is_match(tok, query_stems):
                parts.append(f"{self.highlight_open}{tok}{self.highlight_close}")
            else:
                parts.append(tok)
        snippet = "".join(parts).strip()

        # Surround with ellipses if we cut anything out.
        if start > 0:
            snippet = "… " + snippet
        if end < len(tokens):
            snippet = snippet + " …"
        return snippet

    # ------------------------------------------------------------------
    def generate(
        self,
        text: str,
        query_terms: Iterable[str],
        fallback: Optional[str] = None,
    ) -> str:
        """Return the best snippet for `text` given preprocessed query terms."""
        query_stems = list(query_terms)
        if not text:
            return fallback or ""
        tokens = _split_with_offsets(text)
        if not tokens or not query_stems:
            return fallback if fallback is not None else text[: 200]
        start, end = self._best_window(tokens, query_stems)
        return self._render(tokens, start, end, query_stems) or (fallback or text[:200])
