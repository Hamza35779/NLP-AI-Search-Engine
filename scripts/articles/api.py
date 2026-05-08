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
        "The Flask application exposes both HTML pages and a comprehensive "
        "JSON API. This document enumerates every route, lists their "
        "parameters with default values, and gives the schema of the "
        "JSON responses, including new features in v0.3.0.",
    )

    # 1. Routes
    flow.append(section(styles, "1", "Routes"))
    flow.append(styled_table(
        styles,
        header=("Method", "Path", "Description"),
        rows=[
            ("GET", "/", "Landing page with search form, examples, feature grid."),
            ("GET", "/about", "Project overview, API summary, links."),
            ("GET", "/search", "HTML results page with facets and bookmarks."),
            ("GET", "/api/search", "Ranked results as JSON with filters/sorting."),
            ("GET", "/api/semantic-search", "Semantic search using TF-IDF vectors."),
            ("POST", "/api/batch-search", "Search multiple queries at once (max 20)."),
            ("GET", "/api/autocomplete", "Query autocomplete suggestions."),
            ("GET", "/api/export", "Export results as JSON or CSV."),
            ("GET", "/api/analytics", "Search analytics statistics."),
            ("GET", "/api/top-queries", "Top queries by frequency."),
            ("GET", "/api/related-queries", "Related queries for a given query."),
            ("POST", "/api/documents", "Add a new document to the index."),
            ("DELETE", "/api/documents/<id>", "Remove a document from the index."),
            ("GET", "/api/stats", "Corpus statistics as JSON."),
            ("GET", "/metrics", "Prometheus-compatible metrics."),
            ("GET", "/api/metrics", "JSON metrics (P95, P99, hit rate)."),
            ("GET", "/healthz", "Liveness probe."),
            ("GET", "/readyz", "Readiness check (for Kubernetes)."),
        ],
        col_widths=[2.0 * 28.35, 3.6 * 28.35, 10.4 * 28.35],
    ))

    # 2. GET /api/search
    flow.append(section(styles, "2", "GET /api/search"))
    flow.append(body(
        styles,
        "Run a query and return ranked results as JSON. Supports "
        "facets, sorting, and all query syntax options.",
    ))
    flow.append(subsection(styles, "2.1", "Query parameters"))
    flow.append(small_gap(0.1))
    flow.append(styled_table(
        styles,
        header=("Name", "Type", "Default", "Description"),
        rows=[
            ("q", "string", "required", "Raw query text."),
            ("model", "string", "bm25", "One of bm25, tfidf, semantic."),
            ("k", "int", "10", "Number of results, clamped to 1..50."),
            ("domain", "string", "null", "Filter by domain."),
            ("source", "string", "null", "Filter by source."),
            ("sort", "string", "relevance", "Sort by relevance/title/score_asc."),
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
        '      "source": "machine_learning.txt",',
        "    }",
        "  ],",
        '  "suggestion": null,',
        '  "facets": {...}',
        "}",
    ]))
    flow.append(body(
        styles,
        "If the query returns no results, the "
        "<font face='Courier'>suggestion</font> field contains a "
        "spell-corrected variant produced by the Damerau&ndash;Levenshtein "
        "checker; otherwise it is null.",
    ))

    # 3. GET /api/semantic-search
    flow.append(section(styles, "3", "GET /api/semantic-search"))
    flow.append(body(
        styles,
        "Perform semantic search using TF-IDF vector embeddings. "
        "Returns results ranked by cosine similarity.",
    ))
    flow.append(code_block(styles, [
        'curl "http://127.0.0.1:5000/api/semantic-search?q=machine+learning&k=5"',
    ]))
    flow.append(code_block(styles, [
        "{",
        '  "query": "machine learning",',
        '  "model": "semantic",',
        '  "top_k": 5,',
        '  "results": [...],',
        '  "time_taken": 0.123',
        "}",
    ]))

    # 4. POST /api/batch-search
    flow.append(section(styles, "4", "POST /api/batch-search"))
    flow.append(body(
        styles,
        "Search multiple queries at once (max 20 queries per batch).",
    ))
    flow.append(code_block(styles, [
        'curl -X POST "http://127.0.0.1:5000/api/batch-search" \\',
        '  -H "Content-Type: application/json" \\',
        '  -d \'{"queries": ["ml", "nlp"], "top_k": 5}\'',
    ]))
    flow.append(code_block(styles, [
        "{",
        '  "results": {',
        '    "ml": [...],',
        '    "nlp": [...]',
        "  },",
        '  "query_count": 2,',
        "}",
    ]))

    # 5. GET /api/export
    flow.append(section(styles, "5", "GET /api/export"))
    flow.append(body(
        styles,
        "Export search results in JSON or CSV format.",
    ))
    flow.append(code_block(styles, [
        'curl "http://127.0.0.1:5000/api/export?q=ml&format=csv"',
    ]))

    # 6. GET /api/autocomplete
    flow.append(section(styles, "6", "GET /api/autocomplete"))
    flow.append(body(
        styles,
        "Get autocomplete suggestions for a prefix as you type.",
    ))
    flow.append(code_block(styles, [
        'curl "http://127.0.0.1:5000/api/autocomplete?prefix=ma"',
    ]))
    flow.append(code_block(styles, [
        "{",
        '  "prefix": "ma",',
        '  "suggestions": ["machin", "main", "make"]',
        "}",
    ]))

    # 7. Analytics endpoints
    flow.append(section(styles, "7", "Analytics Endpoints"))
    flow.append(code_block(styles, [
        'curl "http://127.0.0.1:5000/api/analytics"',
        'curl "http://127.0.0.1:5000/api/top-queries"',
        'curl "http://127.0.0.1:5000/api/related-queries?q=ml"',
    ]))

    # 8. Document Management
    flow.append(section(styles, "8", "Document Management"))
    flow.append(body(
        styles,
        "Add or remove documents via API endpoints.",
    ))
    flow.append(code_block(styles, [
        '# Add document (POST)',
        'curl -X POST "http://127.0.0.1:5000/api/documents" \\',
        '  -H "Content-Type: application/json" \\',
        '  -d \'{"title": "Doc", "text": "content"}\'',
        '',
        '# Remove document (DELETE)',
        'curl -X DELETE "http://127.0.0.1:5000/api/documents/1"',
    ]))

    # 9. Monitoring endpoints
    flow.append(section(styles, "9", "Monitoring Endpoints"))
    flow.append(code_block(styles, [
        '# Prometheus metrics',
        'curl "http://127.0.0.1:5000/metrics"',
        '',
        '# JSON metrics',
        'curl "http://127.0.0.1:5000/api/metrics"',
        '',
        '# Health check',
        'curl "http://127.0.0.1:5000/healthz"',
        '',
        '# Readiness check',
        'curl "http://127.0.0.1:5000/readyz"',
    ]))

    # 10. Error handling
    flow.append(section(styles, "10", "Error Handling"))
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

    # 11. Clients
    flow.append(section(styles, "11", "Calling the API"))
    flow.append(subsection(styles, "11.1", "Python"))
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
    flow.append(subsection(styles, "11.2", "JavaScript"))
    flow.append(code_block(styles, [
        "const res = await fetch(",
        "  '/api/search?' + new URLSearchParams({q: 'neural', model: 'bm25'})",
        ");",
        "const data = await res.json();",
        "console.log(data.results);",
    ]))

    return flow
