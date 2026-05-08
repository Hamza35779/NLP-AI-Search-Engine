"""Content for `docs/architecture.pdf` — the system architecture article."""

from __future__ import annotations

import os

from .._pdf_blocks import (  # type: ignore[import-not-found]
    abstract, body, body_tight, bullet_list,
    figure, section, small_gap, styled_table,
    subsection, title_block,
)


DIAGRAM_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "docs", "diagrams")


def _diag(name: str) -> str:
    return os.path.normpath(os.path.join(DIAGRAM_DIR, name))


def build(styles) -> list:
    flow: list = []

    flow += title_block(
        styles,
        title="System Architecture of an NLP Search Engine",
        subtitle="Tokenization &middot; Inverted index &middot; TF&minus;IDF &middot; Okapi BM25",
        author="Hamza Abdul Karim &middot; F23607046",
        date="May 2026",
    )
    flow += abstract(
        styles,
        "We describe the architecture of a small information&#8209;retrieval engine "
        "implemented in pure Python. The system follows the classical sparse&#8209;retrieval "
        "pipeline: documents are tokenized, normalized, and indexed into an inverted "
        "index; queries are parsed into structured form and scored against candidate "
        "documents with TF&#8209;IDF, Okapi BM25, or semantic search (TF&#8209;IDF vectors); "
        "finally, matching documents are filtered, snipped, and returned to the caller "
        "through a single facade. Three front&#8209;ends share this facade: a command&#8209;line "
        "interface, a Flask web application with theme toggle/bookmarks/history, and a "
        "comprehensive JSON API with batch operations and Prometheus metrics. The "
        "discussion below introduces every component, its responsibilities, and its "
        "compile&#8209;time dependencies, accompanied by five reference diagrams.",
    )

    # 1. Introduction
    flow.append(section(styles, "1", "Introduction"))
    flow.append(body(
        styles,
        "Modern web search systems combine sparse and dense retrievers, but the "
        "sparse layer&#8209;rooted in lexical matching, document statistics, and "
        "carefully designed scoring functions&#8209;remains the right starting point "
        "for understanding how search works. This document describes a minimal yet "
        "complete implementation of that layer, written from scratch in roughly "
        "two thousand lines of Python distributed across small, single&#8209;responsibility "
        "files. Each module is intentionally kept under two hundred lines so a "
        "reader can finish it in one sitting.",
    ))
    flow.append(body(
        styles,
        "We begin with a high&#8209;level architectural map (Section&nbsp;2), then "
        "follow the data through indexing (Section&nbsp;3) and querying "
        "(Section&nbsp;4). Section&nbsp;5 documents the static class structure, "
        "Section&nbsp;6 covers the web request flow, and Section&nbsp;7 closes "
        "with a note on persistence.",
    ))

    # 2. Overall architecture
    flow.append(section(styles, "2", "Overall System Architecture"))
    flow.append(body(
        styles,
        "Conceptually, the engine is organised into five horizontal layers. "
        "Inputs arrive from a directory of text files or from a JSON corpus. "
        "An indexing pipeline transforms raw text into an inverted index. "
        "Two ranking models sit on top of that index, exposed through a thin "
        "facade. The search facade adds query parsing, snippet generation, and "
        "spell correction. Finally, two front&#8209;ends &mdash; a CLI and a "
        "Flask app &mdash; consume the facade. Figure&nbsp;1 shows the layout.",
    ))
    flow.append(figure(
        styles, _diag("system_architecture.svg"),
        "Figure 1. The five layers of the search engine and their dependencies.",
    ))

    flow.append(subsection(styles, "2.1", "Module map"))
    flow.append(body_tight(
        styles,
        "Each box in Figure&nbsp;1 corresponds to one Python file under "
        "<font face='Courier'>src/</font>. The module-to-responsibility "
        "mapping is summarised in Table&nbsp;1.",
    ))
    flow.append(small_gap(0.2))

    flow.append(styled_table(
        styles,
        header=("Module", "Responsibility"),
        rows=[
            ("preprocessing.py", "Tokenizer, stop-word filter, Porter stemmer."),
            ("document.py", "Document dataclass and serialization helpers."),
            ("document_loader.py", "Read corpora from a directory or JSON file."),
            ("indexer.py", "InvertedIndex with positional postings."),
            ("tfidf.py", "TF-IDF model with cosine scoring."),
            ("bm25.py", "Okapi BM25 with tunable k1 / b."),
            ("semantic_search.py", "Semantic search with TF-IDF vectors."),
            ("ranker.py", "Lazy facade over the ranking models."),
            ("query_processor.py", "Parse +must, -must-not, phrases, booleans."),
            ("snippet.py", "Best-window snippet with <mark> highlighting."),
            ("spell_check.py", "Damerau-Levenshtein vocabulary lookup."),
            ("analytics.py", "Search analytics tracking."),
            ("autocomplete.py", "Query autocomplete suggestions."),
            ("cache.py", "Search result caching layer."),
            ("metrics.py", "IR metrics + SearchMetrics class."),
            ("persistence.py", "SQLite backend (optional)."),
            ("search_engine.py", "End-to-end SearchEngine facade."),
        ],
        col_widths=[4.4 * 28.35, 11.6 * 28.35],
    ))

    # 3. Indexing pipeline
    flow.append(section(styles, "3", "Indexing Pipeline"))
    flow.append(body(
        styles,
        "The indexing pipeline turns raw text into an inverted index in "
        "five stages, illustrated in Figure&nbsp;2. Stage&nbsp;1 is a "
        "filesystem path that points either at a directory of "
        "<font face='Courier'>.txt</font> files or at a single JSON file. "
        "The DocumentLoader (stage&nbsp;2) "
        "reads the corpus and assigns sequential numeric IDs. The "
        "Preprocessor (stage&nbsp;3) tokenizes each document with a "
        "regular expression, lowercases tokens, drops stop&#8209;words and "
        "tokens shorter than two characters, and finally applies a "
        "compact Porter stemmer. The Indexer (stage&nbsp;4) inserts the "
        "resulting token sequence into the InvertedIndex, populating "
        "three persistent data structures along the way: the postings "
        "themselves, per&#8209;document lengths, and the document "
        "frequency for every term.",
    ))
    flow.append(figure(
        styles, _diag("indexing_pipeline.svg"),
        "Figure 2. Stages and persistent data structures of the indexing pipeline.",
    ))
    flow.append(body(
        styles,
        "From the per&#8209;document lengths the engine derives the "
        "average document length <font face='Courier'>avgdl</font>, "
        "which is consumed at scoring time by Okapi BM25's length "
        "normalization term (Section&nbsp;5).",
    ))

    # 4. Query lifecycle
    flow.append(section(styles, "4", "Query Lifecycle"))
    flow.append(body(
        styles,
        "Figure&nbsp;3 traces a query from the user to a ranked list of "
        "results. The SearchEngine first hands the raw string to the "
        "QueryProcessor, which parses it into four buckets: required "
        "tokens (<font face='Courier'>+term</font>), optional tokens "
        "(bare terms), excluded tokens (<font face='Courier'>-term</font>), "
        "and quoted phrases. The Ranker is then invoked with the union "
        "of the positive bags. It walks the appropriate ranking model "
        "(BM25 by default) over the postings of every query term and "
        "produces a list of candidate <font face='Courier'>(doc_id, score)</font> "
        "pairs. The SearchEngine applies the phrase, must, and "
        "must&#8209;not filters; for each surviving document it asks the "
        "SnippetGenerator to pick the most relevant window in the "
        "original text and to wrap each match in "
        "<font face='Courier'>&lt;mark&gt;</font> tags. The result is a "
        "list of typed <font face='Courier'>SearchResult</font> records "
        "ready for display.",
    ))
    flow.append(figure(
        styles, _diag("query_lifecycle.svg"),
        "Figure 3. Sequence diagram of a single search request.",
        max_width_cm=15.5,
    ))

    # 5. Class structure
    flow.append(section(styles, "5", "Class Structure"))
    flow.append(body(
        styles,
        "The static structure of the engine, simplified to UML, is "
        "shown in Figure&nbsp;4. SearchEngine is the only class that "
        "external code needs to know about; the rest are reachable "
        "through it. Ranker delegates scoring to either TfIdfModel or "
        "BM25Model, both of which read from a shared InvertedIndex. "
        "QueryProcessor is the only component that depends on the "
        "Preprocessor directly &mdash; it shares the same tokenizer "
        "rules as the indexer to ensure that query and document terms "
        "live in the same vocabulary.",
    ))
    flow.append(figure(
        styles, _diag("class_diagram.svg"),
        "Figure 4. Simplified UML class diagram of the engine's core types.",
    ))

    # 6. Web request flow
    flow.append(section(styles, "6", "Web Request Flow"))
    flow.append(body(
        styles,
        "The Flask application creates exactly one SearchEngine "
        "instance at startup. Both the HTML routes "
        "(<font face='Courier'>/</font>, <font face='Courier'>/about</font>, "
        "<font face='Courier'>/search</font>) and the JSON endpoints "
        "(<font face='Courier'>/api/search</font>, "
        "<font face='Courier'>/api/stats</font>, "
        "<font face='Courier'>/healthz</font>) read from this single "
        "in-memory instance, as shown in Figure&nbsp;5. No write "
        "endpoints exist, so the index is effectively immutable for "
        "the lifetime of the process; rebuilding the index requires a "
        "restart or a call to the build script.",
    ))
    flow.append(figure(
        styles, _diag("web_request_flow.svg"),
        "Figure 5. HTML and JSON request paths through the Flask app.",
    ))

    # 7. Persistence
    flow.append(section(styles, "7", "Persistence"))
    flow.append(body(
        styles,
        "<font face='Courier'>SearchEngine.save()</font> pickles the "
        "entire engine &mdash; index, ranker, preprocessor, and "
        "configuration &mdash; to "
        "<font face='Courier'>index_data/engine.pkl</font> by default. "
        "<font face='Courier'>SearchEngine.load()</font> reverses the "
        "operation. For larger corpora this approach should be "
        "replaced with a dedicated on&#8209;disk index format, for "
        "instance one file per posting list, without changing the "
        "public API.",
    ))

    # 8. References
    flow.append(section(styles, "8", "References"))
    flow += bullet_list(styles, [
        "Manning, C.&nbsp;D., Raghavan, P., &amp; Sch&uuml;tze, H. "
        "<i>Introduction to Information Retrieval</i>, Cambridge "
        "University Press, 2008.",
        "Robertson, S., &amp; Zaragoza, H. <i>The Probabilistic "
        "Relevance Framework: BM25 and Beyond</i>. Foundations and "
        "Trends in Information Retrieval, 2009.",
        "Porter, M.&nbsp;F. <i>An Algorithm for Suffix Stripping</i>. "
        "Program, 1980.",
    ])
    return flow
