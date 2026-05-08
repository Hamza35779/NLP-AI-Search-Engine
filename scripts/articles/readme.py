"""Content for `README.pdf` — top-level project overview."""

from __future__ import annotations

import os

from .._pdf_blocks import (  # type: ignore[import-not-found]
    abstract, body, body_tight, bullet_list,
    code_block, figure, section, small_gap,
    styled_table, title_block,
)


DIAGRAM = os.path.normpath(
    os.path.join(os.path.dirname(__file__), "..", "..", "docs",
                 "diagrams", "system_architecture.svg")
)


def build(styles) -> list:
    flow: list = []
    flow += title_block(
        styles,
        title="NLP Search Engine",
        subtitle="A small, hackable information&minus;retrieval engine in pure Python",
        author="Hamza Abdul Karim &middot; F23607046",
        date="May 2026",
    )
    flow += abstract(
        styles,
        "This project implements the classical information&#8209;retrieval "
        "stack &mdash; tokenization, Porter stemming, an inverted index, "
        "and TF&#8209;IDF / Okapi BM25 ranking &mdash; in roughly two thousand "
        "lines of Python. The code is organised into single&#8209;responsibility "
        "files of fewer than two hundred lines each, so it can be read in "
        "one sitting. Features include semantic search with TF&#8209;IDF vectors, "
        "search analytics, query autocomplete, faceted search with filters, "
        "batch operations, and incremental indexing. Three front&#8209;ends share "
        "the same SearchEngine facade: a command&#8209;line interface, a Flask web "
        "application with dark/light theme toggle, and a comprehensive JSON API.",
    )

    # 1. What's inside
    flow.append(section(styles, "1", "What's Inside"))
    flow += bullet_list(styles, [
        "<b>NLP preprocessing</b> &mdash; tokenization, case folding, "
        "stop&#8209;word removal, and a compact Porter stemmer.",
        "<b>Inverted index</b> &mdash; postings carry term frequencies "
        "and positions, enabling phrase queries.",
        "<b>Multiple ranking models</b> &mdash; TF&minus;IDF, BM25, "
        "and semantic search with TF&minus;IDF vectors.",
        "<b>Smart query parsing</b> &mdash; phrases, +must, &minus;exclude, "
        "boolean operators (AND, OR, NOT).",
        "<b>Snippets and highlights</b> &mdash; best&#8209;window selection "
        "with matched&#8209;term highlighting.",
        "<b>Spell suggestions</b> &mdash; Damerau&ndash;Levenshtein "
        "matching against the index vocabulary.",
        "<b>Search analytics</b> &mdash; query tracking, top queries, "
        "related queries, and Prometheus metrics.",
        "<b>Faceted search</b> &mdash; filter by domain, source, score; "
        "sort by relevance, title, or score.",
        "<b>Autocomplete</b> &mdash; real&dash;time suggestions as you type.",
        "<b>Three front&#8209;ends</b> &mdash; CLI, Flask web UI with "
        "theme toggle, bookmarks, history, and comprehensive JSON API.",
    ])

    # 2. Architecture
    flow.append(section(styles, "2", "Architecture at a Glance"))
    flow.append(body(
        styles,
        "The system is organised into five horizontal layers, "
        "shown in Figure&nbsp;1. Inputs flow into the indexing "
        "pipeline; the resulting inverted index is consumed by two "
        "interchangeable ranking models, exposed through a thin "
        "Ranker facade. The SearchEngine ties everything together "
        "and is the single entry point for both the CLI and the web "
        "application. The full set of architectural diagrams is in "
        "<font face='Courier'>docs/architecture.pdf</font>.",
    ))
    flow.append(figure(
        styles, DIAGRAM,
        "Figure 1. System architecture (see docs/architecture.pdf for the full set).",
        max_width_cm=15.5,
    ))

    # 3. Quickstart
    flow.append(section(styles, "3", "Quickstart"))
    flow.append(code_block(styles, [
        "git clone https://github.com/Hamza35779/NLP-AI-Search-Engine.git",
        "cd NLP-AI-Search-Engine",
        "",
        "pip install -r requirements.txt",
        "python scripts/build_index.py",
        "",
        "python cli.py \"machine learning\"      # one-shot CLI",
        "python cli.py                          # CLI in REPL mode",
        "python app.py                          # Flask UI on :5000",
    ]))
    flow.append(body_tight(styles, "Or with Docker:"))
    flow.append(code_block(styles, [
        "docker build -t nlp-search-engine .",
        "docker run --rm -p 5000:5000 nlp-search-engine",
    ]))

    # 4. Demo queries
    flow.append(section(styles, "4", "Demo Queries"))
    flow.append(code_block(styles, [
        "information retrieval",
        "\"natural language\"",
        "ranking +bm25 -neural",
        "neural NOT toy",
    ]))

    # 5. Project layout
    flow.append(section(styles, "5", "Project Layout"))
    flow.append(code_block(styles, [
        "nlp-search-engine/",
        " app.py             Flask web UI (with new endpoints)",
        " cli.py             Argparse CLI",
        " requirements.txt            Python dependencies",
        " pyproject.toml     Packaging + tool config",
        " Dockerfile         Production container",
        " Makefile           Build automation",
        " README.md                  This file",
        " LICENSE                    MIT License",
        "│",
        " src/               Engine source (every file <200 lines)",
        "│   ├── search_engine.py       Main facade (with caching, analytics, metrics)",
        "│   ├── document.py           Document class (with URL/domain support)",
        "│   ├── document_loader.py     Corpus loading + web crawling",
        "│   ├── indexer.py            Inverted index",
        "│   ├── ranker.py             Ranking model wrapper",
        "│   ├── bm25.py               BM25 implementation",
        "│   ├── tfidf.py              TF-IDF implementation",
        "│   ├── semantic_search.py    Semantic search (TF-IDF vectors)",
        "│   ├── preprocessing.py      Tokenization, stemming, stopwords",
        "│   ├── query_processor.py   Query parsing",
        "│   ├── snippet.py            Snippet generation",
        "│   ├── spell_check.py        Spell checker",
        "│   ├── cache.py              Search result caching layer",
        "│   ├── logger.py             Logging configuration",
        "│   ├── metrics.py            IR metrics + SearchMetrics",
        "│   ├── analytics.py          Search analytics tracking",
        "│   ├── autocomplete.py       Query autocomplete suggestions",
        "│   ├── persistence.py        SQLite backend (optional)",
        "│   ├── config.py             Configuration (v0.3.0)",
        "│   └── utils.py              Helper functions",
        "│",
        " templates/                 Jinja2 HTML templates",
        "│   ├── base.html             Base layout (history, bookmarks, theme)",
        "│   ├── index.html            Home page with hero section",
        "│   ├── results.html          Search results (facets, bookmarks)",
        "│   ├── about.html            Project information",
        "│   └── _partials/           Reusable components",
        "│",
        " static/                    CSS, JS, and images",
        "│   ├── css/",
        "│   │   ├── base.css          Design tokens, typography, layout (v2)",
        "│   │   ├── components.css    Search form, cards, badges (v2)",
        "│   │   ├── home.css          Hero, features, steps",
        "│   │   └── results.css      Results page layout (v2)",
        "│   ├── js/",
        "│   │   └── app.js            Search history, bookmarks, theme toggle",
        "│   └── img/                 Logos and favicons",
        "│",
        " tests/                     pytest test suite (25 tests)",
        " scripts/                   Build/indexing scripts",
        " examples/                  Usage examples",
        "└── data/                      Sample corpus",
        "    └── sample_docs/          7 NLP/IR documents",
    ]))

    # 6. Documentation
    flow.append(section(styles, "6", "Documentation"))
    flow.append(small_gap(0.1))
    flow.append(styled_table(
        styles,
        header=("Topic", "Location"),
        rows=[
            ("System overview and diagrams", "docs/architecture.pdf"),
            ("TF-IDF and BM25 in depth", "docs/ranking-models.pdf"),
            ("Semantic search with TF-IDF vectors", "docs/semantic-search.pdf"),
            ("HTTP/JSON API (full reference)", "docs/api.pdf"),
            ("Search analytics and metrics", "docs/analytics.pdf"),
            ("Dev environment and contributing",
             "docs/development.pdf and CONTRIBUTING.pdf"),
            ("Release history", "CHANGELOG.pdf"),
        ],
        col_widths=[7.0 * 28.35, 9.0 * 28.35],
    ))

    # 7. Testing
    flow.append(section(styles, "7", "Testing"))
    flow.append(code_block(styles, ["pytest -q"]))
    flow.append(body(
        styles,
        "The suite is fast (well under a second) and covers "
        "preprocessing, the inverted index, both rankers, the query "
        "parser, snippets, spell suggestions, and the IR metric "
        "helpers.",
    ))

    # 8. New Features in v0.3.0
    flow.append(section(styles, "8", "New Features in v0.3.0"))
    flow += bullet_list(styles, [
        "<b>Semantic Search</b> &mdash; TF-IDF vector embeddings for semantic matching.",
        "<b>Search Analytics</b> &mdash; query tracking, top queries, related queries.",
        "<b>Query Autocomplete</b> &mdash; real-time suggestions as you type.",
        "<b>Faceted Search</b> &mdash; filter by domain, source, score; sort options.",
        "<b>Search History & Bookmarks</b> &mdash; LocalStorage with theme toggle.",
        "<b>Batch Search API</b> &mdash; process up to 20 queries at once.",
        "<b>Metrics & Monitoring</b> &mdash; Prometheus endpoint, health checks.",
        "<b>Incremental Indexing</b> &mdash; SQLite backend for efficient updates.",
    ])

    # 9. License
    flow.append(section(styles, "9", "License"))
    flow.append(body(
        styles,
        "MIT &copy; 2026 Hamza Abdul Karim. See the bundled "
        "<font face='Courier'>LICENSE</font> file for full text.",
    ))

    return flow
