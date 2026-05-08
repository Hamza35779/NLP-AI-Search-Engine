"""Content for `docs/development.pdf` — developer guide."""

from __future__ import annotations

from .._pdf_blocks import (  # type: ignore[import-not-found]
    abstract, body, body_tight, bullet_list,
    code_block, section, small_gap, styled_table,
    subsection, title_block,
)


def build(styles) -> list:
    flow: list = []
    flow += title_block(
        styles,
        title="Development Guide",
        subtitle="Setup, conventions, and contribution workflow",
        author="Hamza Abdul Karim &middot; F23607046",
        date="May 2026",
    )
    flow += abstract(
        styles,
        "This guide describes how to set up a working environment for "
        "the NLP search engine, the conventions the codebase follows, "
        "and the steps required to add a new ranking model or "
        "front&#8209;end. The supplied Makefile and Docker image cover "
        "the common day&#8209;to&#8209;day operations.",
    )

    # 1. Prerequisites
    flow.append(section(styles, "1", "Prerequisites"))
    flow += bullet_list(styles, [
        "Python 3.11 or newer.",
        "<font face='Courier'>git</font>.",
        "<font face='Courier'>make</font> (optional, but the supplied "
        "Makefile shortcuts are convenient).",
    ])

    # 2. Getting started
    flow.append(section(styles, "2", "Getting Started"))
    flow.append(code_block(styles, [
        "git clone https://github.com/AbdulGhani002/nlp-search-engine.git",
        "cd nlp-search-engine",
        "",
        "python -m venv .venv",
        "# Linux/macOS:    source .venv/bin/activate",
        "# Windows (PS):   .venv\\Scripts\\Activate.ps1",
        "",
        "pip install -e \".[dev]\"",
    ]))
    flow.append(body(
        styles,
        "The editable install lets you edit modules under "
        "<font face='Courier'>src/</font> and have the changes picked "
        "up without reinstalling the package.",
    ))

    # 3. Common tasks
    flow.append(section(styles, "3", "Common Tasks"))
    flow.append(small_gap(0.1))
    flow.append(styled_table(
        styles,
        header=("Task", "Command"),
        rows=[
            ("Run the test suite", "pytest -q   (or: make test)"),
            ("Run a one-off CLI search", "python cli.py \"your query\""),
            ("Start the web UI", "python app.py   (or: make run)"),
            ("Rebuild the index", "python scripts/build_index.py"),
            ("Rebuild PDF docs", "python scripts/build_docs.py"),
            ("Lint with Ruff", "make lint"),
            ("Format with Black", "make format"),
            ("Build the Docker image", "make docker"),
        ],
        col_widths=[6.0 * 28.35, 10.0 * 28.35],
    ))

    # 4. Repository layout
    flow.append(section(styles, "4", "Repository Layout"))
    flow.append(code_block(styles, [
        "nlp-search-engine/",
        " app.py                  Flask UI",
        " cli.py                  Argparse CLI",
        " pyproject.toml          Packaging + tool config",
        " Dockerfile              Production container",
        " Makefile                Common commands",
        " data/sample_docs/       Tiny demo corpus",
        " docs/                   PDFs and SVG diagrams",
        " examples/               Standalone usage examples",
        " scripts/                build_index.py, build_docs.py, helpers",
        " src/                    Engine source (every file <200 lines)",
        " static/                 CSS, logos",
        " templates/              Jinja2 templates",
        " tests/                  Pytest suite",
        " .github/                CI workflows",
    ]))

    # 5. Coding conventions
    flow.append(section(styles, "5", "Coding Conventions"))
    flow += bullet_list(styles, [
        "Each source file stays under 200 lines (split when necessary).",
        "Type hints everywhere; modules use "
        "<font face='Courier'>from __future__ import annotations</font>.",
        "Public APIs are exposed through the package facade in "
        "<font face='Courier'>src/__init__.py</font>.",
        "Comments only when the <i>why</i> is non&#8209;obvious; naming "
        "should make the <i>what</i> self&#8209;explanatory.",
    ])

    # 6. Adding a new ranking model
    flow.append(section(styles, "6", "Adding a New Ranking Model"))
    flow.append(body(
        styles,
        "The Ranker is intentionally thin so a new scoring function "
        "is a small change.",
    ))
    flow += bullet_list(styles, [
        "Implement a class in <font face='Courier'>src/&lt;your_model&gt;.py</font> "
        "exposing <font face='Courier'>score(query_terms) -&gt; "
        "List[Tuple[int, float]]</font>.",
        "Register it in <font face='Courier'>src/ranker.py</font>: "
        "extend <font face='Courier'>VALID_MODELS</font>, add a lazy "
        "property, and dispatch in <font face='Courier'>Ranker.rank</font>.",
        "Update <font face='Courier'>docs/ranking-models.pdf</font> "
        "and add a unit test under <font face='Courier'>tests/</font>.",
    ])

    # 7. Adding a new front-end
    flow.append(section(styles, "7", "Adding a New Front-end"))
    flow.append(body_tight(
        styles,
        "The <font face='Courier'>SearchEngine</font> class is "
        "framework&#8209;agnostic. The minimal sequence is:",
    ))
    flow.append(code_block(styles, [
        "from src.config import EngineConfig",
        "from src.search_engine import SearchEngine",
        "",
        "engine = SearchEngine(EngineConfig(), model=\"bm25\")",
        "engine.index_corpus(\"data/sample_docs\")",
        "results = engine.search(\"your query\", top_k=5)",
    ]))

    # 8. Testing strategy
    flow.append(section(styles, "8", "Testing Strategy"))
    flow += bullet_list(styles, [
        "Unit tests sit next to the module they exercise in "
        "<font face='Courier'>tests/test_*.py</font>.",
        "End&#8209;to&#8209;end tests drive the SearchEngine through "
        "realistic queries (see <font face='Courier'>tests/test_search.py</font>).",
        "The suite must remain fast (well under a second locally) so "
        "the contributor feedback loop stays painless.",
    ])

    # 9. Releasing
    flow.append(section(styles, "9", "Releasing"))
    flow += bullet_list(styles, [
        "Bump <font face='Courier'>__version__</font> in "
        "<font face='Courier'>src/__init__.py</font> and the version "
        "in <font face='Courier'>pyproject.toml</font>.",
        "Move the <i>Unreleased</i> section in the changelog under "
        "the new version.",
        "Tag the commit (<font face='Courier'>git tag -a vX.Y.Z -m "
        "\"Release vX.Y.Z\"</font>) and push the tag.",
        "CI runs the test suite on the tagged commit.",
    ])

    return flow
