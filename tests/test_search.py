"""End-to-end tests for the SearchEngine facade."""

from src.search_engine import SearchEngine


def test_basic_query_returns_relevant_doc(engine):
    results = engine.search("machine learning")
    assert results, "expected at least one result"
    titles = [r.title.lower() for r in results]
    assert any("machine" in t or "nlp" in t for t in titles)


def test_top_k_limits_results(engine):
    results = engine.search("learning", top_k=1)
    assert len(results) <= 1


def test_phrase_filter_excludes_unrelated_docs(engine):
    # The exact phrase "natural language" only appears in one doc.
    results = engine.search('"natural language"')
    assert results
    assert any("nlp" in r.title.lower() for r in results)


def test_must_not_filters_results(engine):
    # Force-exclude "machine" — only the IR document should remain plausible.
    results = engine.search("learning -machine")
    for r in results:
        assert "machine" not in r.snippet.lower()


def test_switching_models_still_returns_results(small_corpus):
    eng = SearchEngine(model="tfidf").index_documents(small_corpus)
    results = eng.search("information retrieval")
    assert results
    assert results[0].score > 0


def test_spell_suggestion_for_typo(engine):
    suggestion = engine.suggest_query("machne lerning")
    assert suggestion is not None
    assert suggestion != "machne lerning"


def test_search_returns_search_results_with_snippet(engine):
    results = engine.search("language")
    assert results
    first = results[0]
    assert first.score > 0
    assert first.snippet
    # The highlight markup should appear when there is a term match.
    assert "<mark>" in first.snippet
