"""Unit tests for the preprocessing pipeline."""

from src.preprocessing import Preprocessor, porter_stem


def test_tokenizer_lowercases_and_strips_punctuation(preprocessor):
    tokens = preprocessor.tokenize("Hello, World! NLP is great.")
    assert tokens == ["hello", "world", "nlp", "is", "great"]


def test_normalize_drops_stopwords_and_short_tokens(preprocessor):
    tokens = preprocessor.normalize(["the", "a", "in", "amazing", "x"])
    # Stop-words and the single-letter "x" are dropped; "amazing" stays.
    assert "the" not in tokens
    assert "a" not in tokens
    assert "x" not in tokens
    assert tokens, "non stop-words should be retained"


def test_process_returns_stems():
    preprocessor = Preprocessor()
    out = preprocessor.process("running runs ran")
    # Stemming should collapse "running" and "runs" to a shared stem;
    # English's irregular "ran" is left alone by the compact Porter rules.
    assert len(set(out)) <= 2


def test_porter_stem_basic():
    assert porter_stem("connections") in {"connect", "connection"}
    assert porter_stem("running") in {"run", "runn"}
    assert porter_stem("relational") in {"relate", "relational", "relat"}


def test_porter_stem_short_word_unchanged():
    assert porter_stem("ab") == "ab"
    assert porter_stem("a") == "a"


def test_stopword_set_includes_common_words(preprocessor):
    sw = preprocessor.stopwords
    for word in ("the", "and", "is", "a", "of"):
        assert word in sw
