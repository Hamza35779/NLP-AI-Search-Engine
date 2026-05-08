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
        "one sitting. Two front&#8209;ends share the same SearchEngine "
        "facade: a command&#8209;line interface and a Flask web "
        "application that also exposes a JSON API. The system was built "
        "as an NLP coursework project and is also a usable search engine "
        "for small corpora.",
    )

    # 1. What's inside
    flow.append(section(styles, "1", "What's Inside"))
    flow += bullet_list(styles, [
        "<b>NLP preprocessing</b> &mdash; tokenization, case folding, "
        "stop&#8209;word removal, and a compact Porter stemmer.",
        "<b>Inverted index</b> &mdash; postings carry term frequencies "
        "and positions, enabling phrase queries.",
        "<b>TF&minus;IDF and BM25</b> &mdash; two interchangeable rankers; "
        "BM25 has tunable <i>k1</i> and <i>b</i> parameters.",
        "<b>Snippets and highlights</b> &mdash; best&#8209;window selection "
        "with matched&#8209;term highlighting.",
        "<b>Spell suggestions</b> &mdash; Damerau&ndash;Levenshtein "
        "matching against the index vocabulary.",
        "<b>Two front&#8209;ends</b> &mdash; argparse CLI and a Flask "
        "web application with a JSON API at "
        "<font face='Courier'>/api/search</font>.",
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
        "git clone https://github.com/AbdulGhani002/nlp-search-engine.git",
        "cd nlp-search-engine",
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
        " app.py             Flask web UI",
        " cli.py             Argparse CLI",
        " pyproject.toml     Packaging + tool configuration",
        " Dockerfile         Production container",
        " Makefile           Common commands",
        " data/sample_docs/  Tiny NLP-themed corpus",
        " docs/              PDFs and SVG diagrams",
        " examples/          Standalone usage examples",
        " scripts/           build_index.py, build_docs.py",
        " src/               Engine source (every file <200 lines)",
        " static/            CSS bundle and SVG brand assets",
        " templates/         Jinja2 templates for the web UI",
        " tests/             Pytest suite",
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
            ("HTTP/JSON API", "docs/api.pdf"),
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

    # 8. License
    flow.append(section(styles, "8", "License"))
    flow.append(body(
        styles,
        "MIT &copy; 2026 Hamza Abdul Karim. See the bundled "
        "<font face='Courier'>LICENSE</font> file for full text.",
    ))

    return flow
