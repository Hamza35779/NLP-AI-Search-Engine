"""Inverted-index construction.

The index maps each term to a posting list. A posting holds the document ID,
the term frequency in that document, and the positions where the term
appears (positions enable phrase queries).

The class also tracks document-level statistics (length, unique vocabulary)
that the rankers consume.
"""

from __future__ import annotations

from collections import defaultdict
from typing import Dict, Iterable, List, Optional, Tuple

from .config import DEFAULT_CONFIG, EngineConfig
from .document import Document
from .preprocessing import Preprocessor


# A single posting is (doc_id, term_freq, [positions])
Posting = Tuple[int, int, List[int]]


class InvertedIndex:
    """Builds and stores an inverted index over a corpus."""

    def __init__(
        self,
        config: Optional[EngineConfig] = None,
        preprocessor: Optional[Preprocessor] = None,
    ) -> None:
        self.config = config or DEFAULT_CONFIG
        self.preprocessor = preprocessor or Preprocessor(self.config)

        self._postings: Dict[str, List[Posting]] = defaultdict(list)
        self._documents: Dict[int, Document] = {}
        self._doc_lengths: Dict[int, int] = {}
        self._term_doc_count: Dict[str, int] = defaultdict(int)
        self._total_tokens: int = 0

    # ----- construction ----------------------------------------------------
    def add_document(self, doc: Document) -> None:
        """Tokenize `doc`, append its postings, update stats."""
        if doc.doc_id in self._documents:
            raise ValueError(f"Duplicate doc_id {doc.doc_id}")

        tokens = self.preprocessor.process(doc.text)
        if not tokens:
            # Still keep the doc so it shows up in listings, but with empty index.
            doc.tokens = []
            self._documents[doc.doc_id] = doc
            self._doc_lengths[doc.doc_id] = 0
            return

        positions: Dict[str, List[int]] = defaultdict(list)
        for pos, term in enumerate(tokens):
            positions[term].append(pos)

        for term, pos_list in positions.items():
            self._postings[term].append((doc.doc_id, len(pos_list), pos_list))
            self._term_doc_count[term] += 1

        doc.tokens = tokens
        self._documents[doc.doc_id] = doc
        self._doc_lengths[doc.doc_id] = len(tokens)
        self._total_tokens += len(tokens)

    def build(self, documents: Iterable[Document]) -> "InvertedIndex":
        for doc in documents:
            self.add_document(doc)
        return self

    # ----- read-side accessors --------------------------------------------
    @property
    def num_documents(self) -> int:
        return len(self._documents)

    @property
    def vocabulary(self) -> List[str]:
        return list(self._postings.keys())

    @property
    def avg_doc_length(self) -> float:
        if not self._doc_lengths:
            return 0.0
        return self._total_tokens / len(self._doc_lengths)

    def document(self, doc_id: int) -> Document:
        return self._documents[doc_id]

    def all_documents(self) -> List[Document]:
        return list(self._documents.values())

    def doc_length(self, doc_id: int) -> int:
        return self._doc_lengths.get(doc_id, 0)

    def postings(self, term: str) -> List[Posting]:
        return self._postings.get(term, [])

    def doc_frequency(self, term: str) -> int:
        return self._term_doc_count.get(term, 0)

    def term_frequency(self, term: str, doc_id: int) -> int:
        for did, tf, _pos in self._postings.get(term, ()):
            if did == doc_id:
                return tf
        return 0

    def positions(self, term: str, doc_id: int) -> List[int]:
        for did, _tf, pos in self._postings.get(term, ()):
            if did == doc_id:
                return pos
        return []

    def documents_containing(self, term: str) -> List[int]:
        return [did for did, _tf, _pos in self._postings.get(term, ())]

    # ----- diagnostics -----------------------------------------------------
    def stats(self) -> Dict[str, float]:
        return {
            "documents": float(self.num_documents),
            "vocabulary_size": float(len(self._postings)),
            "total_tokens": float(self._total_tokens),
            "avg_doc_length": self.avg_doc_length,
        }
