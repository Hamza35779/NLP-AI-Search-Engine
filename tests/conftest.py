"""Shared pytest fixtures."""

from __future__ import annotations

import os
import sys

import pytest

# Make the `src` package importable when running ``pytest`` from the repo root.
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from src.config import EngineConfig  # noqa: E402
from src.document import Document  # noqa: E402
from src.preprocessing import Preprocessor  # noqa: E402
from src.search_engine import SearchEngine  # noqa: E402


@pytest.fixture
def small_corpus():
    return [
        Document(
            doc_id=0,
            title="Information Retrieval",
            text=(
                "Information retrieval is the science of searching for "
                "information in documents and ranking them by relevance."
            ),
        ),
        Document(
            doc_id=1,
            title="Machine Learning",
            text=(
                "Machine learning teaches computers to learn from data. "
                "Common methods include linear regression and neural networks."
            ),
        ),
        Document(
            doc_id=2,
            title="NLP",
            text=(
                "Natural language processing combines linguistics and machine "
                "learning so that computers can understand human language."
            ),
        ),
    ]


@pytest.fixture
def preprocessor():
    return Preprocessor(EngineConfig())


@pytest.fixture
def engine(small_corpus):
    eng = SearchEngine()
    eng.index_documents(small_corpus)
    return eng
