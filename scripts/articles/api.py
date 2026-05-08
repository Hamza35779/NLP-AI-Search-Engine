"""Content for `docs/api.pdf` — HTTP API reference."""

from __future__ import annotations

from .._pdf_blocks import (  # type: ignore[import-not-found]
    abstract, body, code_block, section,
    small_gap, styled_table, subsection, title_block,
)


def build(styles) -> list:
    flow: list = []
    flow += title_block(
        styles,
        title="HTTP API Reference",
        subtitle="Routes, parameters, and response shapes",
        author="Hamza Abdul Karim &middot; F23607046",
        date="May 2026",
    )
    flow += abstract(
        styles,
        "The Flask application exposes both HTML pages and a small "
        "JSON API. This document enumerates every route, lists their "
        "parameters with default values, and gives the schema of the "
        "JSON responses.",
    )

    flow.append(section(styles, "1", "Routes"))
    flow.append(styled_table(
        styles,
        header=("Method", "Path", "Description"),
        rows=[
            ("GET", "/",
             "Landing page with search form, examples, feature grid."),
            ("GET", "/about",
             "Project overview, API summary, links."),
            ("GET", "/search",
             "HTML results page."),
            ("GET", "/api/search",
             "Ranked results as JSON."),
            ("GET", "/api/stats",
             "Corpus statistics as JSON."),
            ("GET", "/healthz",
             "Liveness probe."),
        ],
        col_widths=[2.0 * 28.35, 3.6 * 28.35, 10.4 * 28.35],
    ))

    # /api/search
    flow.append(section(styles, "2", "GET /api/search"))
    flow.append(body(
        styles,
        "Run a query and return ranked results as JSON. The route "
        "parses bare terms, required terms (<font face='Courier'>+term</font>), "
        "excluded terms (<font face='Courier'>-term</font>), quoted "
        "phrases, and the boolean operators "
        "<font face='Courier'>AND</font> / "
        "<font face='Courier'>OR</font> / "
        "<font face='Courier'>NOT</font>.",
    ))

    flow.append(subsection(styles, "2.1", "Query parameters"))
    flow.append(small_gap(0.1))
    flow.append(styled_table(
        styles,
        header=("Name", "Type", "Default", "Description"),
        rows=[
            ("q", "string", "required", "Raw query text."),
            ("model", "string", "bm25", "One of bm25 or tfidf."),
            ("k", "int", "10", "Number of results, clamped to 1..50."),
        ],
        col_widths=[2.0 * 28.35, 2.0 * 28.35, 2.4 * 28.35, 9.6 * 28.35],
    ))

    flow.append(subsection(styles, "2.2", "Example"))
    flow.append(code_block(styles, [
        'curl "http://127.0.0.1:5000/api/search?q=machine+learning&model=bm25&k=3"',
    ]))

    flow.append(subsection(styles, "2.3", "Response shape"))
    flow.append(code_block(styles, [
        "{",
        '  "query": "machine learning",',
        '  "model": "bm25",',
        '  "top_k": 3,',
        '  "results": [',
        "    {",
        '      "doc_id": 1,',
        '      "title": "machine learning",',
        '      "snippet": "<mark>Machine</mark> <mark>learning</mark> ...",',
        '      "score": 3.59904,',
        '      "source": "machine_learning.txt"',
        "    }",
        "  ],",
        '  "suggestion": null',
        "}",
    ]))
    flow.append(body(
        styles,
        "If the query returns no results, the "
        "<font face='Courier'>suggestion</font> field contains a "
        "spell-corrected variant produced by the Damerau&ndash;Levenshtein "
        "checker; otherwise it is null.",
    ))

    # /api/stats
    flow.append(section(styles, "3", "GET /api/stats"))
    flow.append(body(
        styles,
        "Returns counters describing the loaded index.",
    ))
    flow.append(code_block(styles, [
        "{",
        '  "documents": 7,',
        '  "vocabulary_size": 305,',
        '  "total_tokens": 482,',
        '  "avg_doc_length": 68.85,',
        '  "model": "bm25"',
        "}",
    ]))

    # /healthz
    flow.append(section(styles, "4", "GET /healthz"))
    flow.append(body(
        styles,
        "Lightweight liveness check, suitable for Docker or Kubernetes "
        "probes.",
    ))
    flow.append(code_block(styles, [
        "{",
        '  "status": "ok",',
        '  "documents": 7',
        "}",
    ]))

    # Error handling
    flow.append(section(styles, "5", "Error Handling"))
    flow.append(styled_table(
        styles,
        header=("Condition", "Response"),
        rows=[
            ("Unknown model", '400 with {"error": "unknown model \'X\'"}'),
            ("Missing q", "200 with empty results"),
            ("Out-of-range k", "Silently clamped to [1, 50]"),
        ],
        col_widths=[5.0 * 28.35, 11.0 * 28.35],
    ))

    # Clients
    flow.append(section(styles, "6", "Calling the API"))
    flow.append(subsection(styles, "6.1", "Python"))
    flow.append(code_block(styles, [
        "import requests",
        "",
        'resp = requests.get(',
        '    "http://127.0.0.1:5000/api/search",',
        '    params={"q": "neural networks", "model": "tfidf", "k": 5},',
        "    timeout=5,",
        ")",
        "for hit in resp.json()[\"results\"]:",
        '    print(f"{hit[\\"score\\"]:6.3f}  {hit[\\"title\\"]}")',
    ]))

    flow.append(subsection(styles, "6.2", "JavaScript"))
    flow.append(code_block(styles, [
        "const res = await fetch(",
        "  '/api/search?' + new URLSearchParams({q: 'neural', model: 'bm25'})",
        ");",
        "const data = await res.json();",
        "console.log(data.results);",
    ]))

    return flow
