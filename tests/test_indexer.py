"""Unit tests for the inverted index."""

from src.document import Document
from src.indexer import InvertedIndex


def _build(docs):
    return InvertedIndex().build(docs)


def test_index_records_basic_stats(small_corpus):
    idx = _build(small_corpus)
    stats = idx.stats()
    assert stats["documents"] == len(small_corpus)
    assert stats["vocabulary_size"] > 0
    assert stats["avg_doc_length"] > 0


def test_postings_contain_expected_documents(small_corpus):
    idx = _build(small_corpus)
    # All three docs talk about "learning" or "language" in some form.
    learning_docs = idx.documents_containing("learn")
    assert 1 in learning_docs and 2 in learning_docs


def test_term_frequency_round_trip():
    doc = Document(
        doc_id=0,
        title="t",
        text="alpha beta alpha gamma alpha",
    )
    idx = _build([doc])
    assert idx.term_frequency("alpha", 0) == 3
    assert idx.term_frequency("beta", 0) == 1
    assert idx.term_frequency("missing", 0) == 0


def test_positions_match_token_indices():
    doc = Document(doc_id=0, title="t", text="alpha beta alpha gamma")
    idx = _build([doc])
    positions = idx.positions("alpha", 0)
    assert positions == sorted(positions)
    assert len(positions) == 2


def test_duplicate_doc_ids_are_rejected():
    docs = [
        Document(doc_id=5, title="a", text="hello world"),
        Document(doc_id=5, title="b", text="another doc"),
    ]
    idx = InvertedIndex()
    idx.add_document(docs[0])
    try:
        idx.add_document(docs[1])
    except ValueError:
        return
    raise AssertionError("Expected ValueError for duplicate doc_id")


def test_empty_document_is_kept_but_unindexed():
    idx = _build([Document(doc_id=0, title="empty", text="")])
    assert idx.num_documents == 1
    assert idx.doc_length(0) == 0
