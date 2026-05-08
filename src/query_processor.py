"""Parse a raw query string into structured tokens.

Supports:
  * Quoted phrases:   "machine learning"
  * Required terms:   +keyword
  * Excluded terms:   -keyword
  * Boolean operators between bare terms: AND / OR / NOT
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List, Optional

from .config import EngineConfig
from .preprocessing import Preprocessor


_OPERATORS = {"AND", "OR", "NOT"}
_TOKEN_RE = re.compile(r'"[^"]+"|\+\S+|-\S+|\S+')


@dataclass
class ParsedQuery:
    """Structured representation of a user query."""

    raw: str
    must_terms: List[str] = field(default_factory=list)        # +term
    should_terms: List[str] = field(default_factory=list)      # bare term
    must_not_terms: List[str] = field(default_factory=list)    # -term / NOT term
    phrases: List[List[str]] = field(default_factory=list)     # "two words"
    operator: str = "OR"  # default match mode for `should_terms`

    @property
    def all_positive_terms(self) -> List[str]:
        seen: set[str] = set()
        merged: List[str] = []
        for bag in (self.must_terms, self.should_terms):
            for term in bag:
                if term not in seen:
                    seen.add(term)
                    merged.append(term)
        for phrase in self.phrases:
            for term in phrase:
                if term not in seen:
                    seen.add(term)
                    merged.append(term)
        return merged

    def is_empty(self) -> bool:
        return not (
            self.must_terms or self.should_terms or self.must_not_terms or self.phrases
        )


class QueryProcessor:
    """Tokenize raw queries into a `ParsedQuery`."""

    def __init__(
        self,
        preprocessor: Preprocessor,
        config: Optional[EngineConfig] = None,
    ) -> None:
        self.preprocessor = preprocessor
        self.config = config or preprocessor.config

    def parse(self, raw_query: str) -> ParsedQuery:
        parsed = ParsedQuery(raw=raw_query or "")
        if not raw_query or not raw_query.strip():
            return parsed

        tokens = _TOKEN_RE.findall(raw_query)
        i = 0
        next_negate = False
        while i < len(tokens):
            tok = tokens[i]
            upper = tok.upper()

            if upper == "NOT":
                next_negate = True
                i += 1
                continue
            if upper == "AND":
                parsed.operator = "AND"
                i += 1
                continue
            if upper == "OR":
                parsed.operator = "OR"
                i += 1
                continue

            if tok.startswith('"') and tok.endswith('"') and len(tok) > 2:
                phrase_tokens = self.preprocessor.process(tok.strip('"'))
                if phrase_tokens:
                    if next_negate:
                        parsed.must_not_terms.extend(phrase_tokens)
                    else:
                        parsed.phrases.append(phrase_tokens)
                next_negate = False
                i += 1
                continue

            if tok.startswith("+") and len(tok) > 1:
                processed = self.preprocessor.process(tok[1:])
                parsed.must_terms.extend(processed)
                next_negate = False
                i += 1
                continue

            if tok.startswith("-") and len(tok) > 1:
                processed = self.preprocessor.process(tok[1:])
                parsed.must_not_terms.extend(processed)
                next_negate = False
                i += 1
                continue

            processed = self.preprocessor.process(tok)
            if next_negate:
                parsed.must_not_terms.extend(processed)
                next_negate = False
            else:
                parsed.should_terms.extend(processed)
            i += 1

        return parsed
