"""Document container used everywhere in the pipeline."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse


@dataclass
class Document:
    """A single document held in the corpus.

    Attributes
    ----------
    doc_id:
        Unique numeric ID assigned at index time.
    title:
        Short human-readable title shown in result listings.
    text:
        Full document body — used for snippet generation.
    source:
        URL or path the document came from.
    url:
        Canonical URL for web documents (used for display & linking).
    metadata:
        Free-form extra info (author, date, tags, domain, etc.).
    tokens:
        Cached preprocessed tokens; populated by the indexer.
    inbound_links:
        Number of inbound links (for PageRank-like scoring).
    """

    doc_id: int
    title: str
    text: str
    source: Optional[str] = None
    url: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    tokens: List[str] = field(default_factory=list)
    inbound_links: int = 0

    @property
    def display_url(self) -> str:
        """Return a clean URL for display purposes."""
        if self.url:
            parsed = urlparse(self.url)
            return f"{parsed.netloc}{parsed.path}" if parsed.netloc else self.url
        if self.source:
            return self.source
        return "Unknown source"

    @property
    def domain(self) -> str:
        """Extract domain from URL or source."""
        url_to_check = self.url or self.source or ""
        parsed = urlparse(url_to_check)
        return parsed.netloc or "local"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "doc_id": self.doc_id,
            "title": self.title,
            "text": self.text,
            "source": self.source,
            "url": self.url,
            "metadata": dict(self.metadata),
            "inbound_links": self.inbound_links,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Document":
        return cls(
            doc_id=int(data["doc_id"]),
            title=str(data.get("title", "")),
            text=str(data.get("text", "")),
            source=data.get("source"),
            url=data.get("url"),
            metadata=dict(data.get("metadata", {})),
            inbound_links=int(data.get("inbound_links", 0)),
        )

    def short_preview(self, max_chars: int = 240) -> str:
        body = (self.text or "").strip().replace("\n", " ")
        if len(body) <= max_chars:
            return body
        return body[: max_chars - 1].rstrip() + "…"
