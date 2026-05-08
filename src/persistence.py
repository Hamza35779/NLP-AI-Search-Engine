"""Alternative persistence backends for the index."""

from __future__ import annotations

import json
import sqlite3
from typing import Dict, List, Optional, Tuple

from .document import Document


class SQLiteIndexStore:
    """Store index in SQLite for efficient incremental updates."""

    def __init__(self, db_path: str = "index_data/index.db") -> None:
        self.db_path = db_path
        self._init_db()

    def _init_db(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS documents (
                    doc_id INTEGER PRIMARY KEY,
                    title TEXT NOT NULL,
                    text TEXT NOT NULL,
                    source TEXT,
                    url TEXT,
                    metadata TEXT,
                    inbound_links INTEGER DEFAULT 0
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS postings (
                    term TEXT NOT NULL,
                    doc_id INTEGER NOT NULL,
                    term_freq INTEGER NOT NULL,
                    positions TEXT NOT NULL,
                    PRIMARY KEY (term, doc_id)
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_postings_term ON postings(term)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_postings_doc ON postings(doc_id)")
            conn.commit()

    def add_document(self, doc: Document, tokens: List[str]) -> None:
        """Add or update a document and its postings."""
        with sqlite3.connect(self.db_path) as conn:
            # Insert/update document
            conn.execute("""
                INSERT OR REPLACE INTO documents
                (doc_id, title, text, source, url, metadata, inbound_links)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                doc.doc_id, doc.title, doc.text,
                doc.source, doc.url,
                json.dumps(doc.metadata),
                doc.inbound_links,
            ))

            # Remove old postings for this document
            conn.execute("DELETE FROM postings WHERE doc_id = ?", (doc.doc_id,))

            # Build and insert postings
            term_counts: Dict[str, int] = {}
            term_positions: Dict[str, List[int]] = {}
            for pos, term in enumerate(tokens):
                term_counts[term] = term_counts.get(term, 0) + 1
                if term not in term_positions:
                    term_positions[term] = []
                term_positions[term].append(pos)

            for term, tf in term_counts.items():
                conn.execute("""
                    INSERT INTO postings (term, doc_id, term_freq, positions)
                    VALUES (?, ?, ?, ?)
                """, (
                    term, doc.doc_id, tf,
                    json.dumps(term_positions[term]),
                ))

            conn.commit()

    def remove_document(self, doc_id: int) -> bool:
        """Remove a document and its postings."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "DELETE FROM documents WHERE doc_id = ?",
                (doc_id,)
            )
            conn.execute("DELETE FROM postings WHERE doc_id = ?", (doc_id,))
            conn.commit()
            return cursor.rowcount > 0

    def get_all_documents(self) -> List[Document]:
        """Retrieve all documents."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM documents")
            rows = cursor.fetchall()

            return [
                Document(
                    doc_id=row["doc_id"],
                    title=row["title"],
                    text=row["text"],
                    source=row["source"],
                    url=row["url"],
                    metadata=json.loads(row["metadata"]) if row["metadata"] else {},
                    inbound_links=row["inbound_links"],
                )
                for row in rows
            ]

    def get_postings(self, term: str) -> List[Tuple[int, int, List[int]]]:
        """Get postings for a term."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT doc_id, term_freq, positions FROM postings WHERE term = ?",
                (term,)
            )
            return [
                (row[0], row[1], json.loads(row[2]))
                for row in cursor.fetchall()
            ]

    def get_doc_frequency(self, term: str) -> int:
        """Get document frequency for a term."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT COUNT(*) FROM postings WHERE term = ?",
                (term,)
            )
            return cursor.fetchone()[0]

    def get_vocabulary(self) -> List[str]:
        """Get all terms in the vocabulary."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT DISTINCT term FROM postings")
            return [row[0] for row in cursor.fetchall()]

    def get_doc_count(self) -> int:
        """Get total document count."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM documents")
            return cursor.fetchone()[0]

    def close(self) -> None:
        """Close the connection (no-op for context manager pattern)."""
        pass
