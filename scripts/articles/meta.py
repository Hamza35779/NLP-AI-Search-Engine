"""Content for the smaller meta PDFs: contributing, changelog, CoC, security."""

from __future__ import annotations

from .._pdf_blocks import (  # type: ignore[import-not-found]
    abstract, body, body_tight, bullet_list,
    code_block, section, small_gap, styled_table,
    title_block,
)


# --------------------------------------------------------------------- contrib
def build_contributing(styles) -> list:
    f: list = []
    f += title_block(
        styles,
        title="Contributing to the NLP Search Engine",
        subtitle="Ground rules, workflow, and review checklist",
        author="Hamza Abdul Karim &middot; F23607046",
        date="May 2026",
    )
    f += abstract(
        styles,
        "Thank you for considering a contribution. This is a "
        "teaching&#8209;quality project, so changes that keep the code "
        "small and easy to read are especially welcome. The sections "
        "below describe the ground rules, how to set up an environment, "
        "and the review checklist a pull request should satisfy.",
    )

    f.append(section(styles, "1", "Ground Rules"))
    f += bullet_list(styles, [
        "<b>Small files.</b> Each source file in "
        "<font face='Courier'>src/</font> stays under 200 lines.",
        "<b>No frameworks where stdlib suffices.</b> Pulling in a "
        "heavyweight dependency requires a strong justification.",
        "<b>Tests stay fast.</b> The pytest suite must run in well "
        "under one second locally.",
        "<b>Be kind.</b> See the bundled Code of Conduct.",
    ])

    f.append(section(styles, "2", "Setting Up"))
    f.append(code_block(styles, [
        "git clone https://github.com/AbdulGhani002/nlp-search-engine.git",
        "cd nlp-search-engine",
        "python -m venv .venv && source .venv/bin/activate",
        "pip install -e \".[dev]\"",
        "pre-commit install",
    ]))

    f.append(section(styles, "3", "Workflow"))
    f += bullet_list(styles, [
        "Open an issue describing the change. Skip this for trivial "
        "one&#8209;line fixes.",
        "Create a feature branch: "
        "<font face='Courier'>git checkout -b feat/short-name</font>.",
        "Write the code <i>and</i> the matching test(s).",
        "Run the suite: <font face='Courier'>pytest -q</font>.",
        "Open a pull request against <font face='Courier'>main</font> "
        "and fill out the template.",
    ])

    f.append(section(styles, "4", "Pull Request Checklist"))
    f += bullet_list(styles, [
        "Every modified source file is still under 200 lines.",
        "<font face='Courier'>pytest -q</font> passes locally.",
        "Public API changes are reflected in the relevant PDF under "
        "<font face='Courier'>docs/</font>.",
        "<font face='Courier'>CHANGELOG.pdf</font> updated under the "
        "<i>Unreleased</i> section if user&#8209;visible.",
        "Commit messages follow Conventional Commits "
        "(<font face='Courier'>feat:</font>, "
        "<font face='Courier'>fix:</font>, "
        "<font face='Courier'>docs:</font>...).",
    ])

    return f


# --------------------------------------------------------------------- changelog
def build_changelog(styles) -> list:
    f: list = []
    f += title_block(
        styles,
        title="Release History",
        subtitle="Notable changes between versions",
        author="Hamza Abdul Karim &middot; F23607046",
        date="May 2026",
    )
    f += abstract(
        styles,
        "This document records the user&#8209;visible changes to the "
        "project. The format is loosely based on the "
        "<i>Keep a Changelog</i> convention; versioning follows "
        "Semantic Versioning.",
    )

    f.append(section(styles, "1", "Unreleased"))
    f.append(small_gap(0.1))
    f += bullet_list(styles, [
        "Semantic search using TF-IDF vectors as lightweight embeddings.",
        "Search analytics tracking with query history and statistics.",
        "Query autocomplete API with real-time suggestions.",
        "Document management API (add/remove documents via API).",
        "Related queries feature to discover similar search terms.",
        "Enhanced web UI with autocomplete and related queries.",
        "New API endpoints: /api/semantic-search, /api/autocomplete, "
        "/api/analytics, /api/top-queries, /api/related-queries.",
        "Updated version to 0.3.0 with new features.",
    ])

    f.append(section(styles, "2", "Version 0.2.0 &mdash; May 2026"))
    f.append(body_tight(styles, "<b>Added</b>"))
    f += bullet_list(styles, [
        "Brand identity: SVG logo and favicon.",
        "Modular CSS bundle "
        "(<i>base, components, home, results</i>).",
        "<font face='Courier'>/about</font> page describing the "
        "project and API.",
        "<font face='Courier'>/healthz</font> liveness endpoint.",
        "Five black&#8209;and&#8209;white SVG architecture diagrams.",
        "Five reference PDFs replacing the previous markdown docs.",
    ])
    f.append(body_tight(styles, "<b>Changed</b>"))
    f += bullet_list(styles, [
        "Polished search form, results page, and result cards.",
        "Sidebar on the results page now shows the parsed query, "
        "index stats, and operator help.",
        "Redesigned hero with a feature grid and a how&#8209;it&#8209;works strip.",
    ])

    f.append(section(styles, "3", "Version 0.1.0 &mdash; May 2026"))
    f.append(body_tight(styles, "<b>Added</b>"))
    f += bullet_list(styles, [
        "Core NLP preprocessing.",
        "Inverted index with positions and per&#8209;document statistics.",
        "TF&minus;IDF (cosine) and Okapi BM25 ranking models.",
        "Query parser supporting <font face='Courier'>+must</font>, "
        "<font face='Courier'>-must-not</font>, "
        "<font face='Courier'>\"phrase\"</font>, and boolean operators.",
        "Snippet generator with highlighting.",
        "Damerau&ndash;Levenshtein spell suggestions.",
        "IR metric helpers: precision/recall@k, MAP, MRR, nDCG@k.",
        "CLI with one&#8209;shot and REPL modes.",
        "Flask web UI with HTML pages and a JSON API.",
        "Pytest suite with 25 tests.",
        "Sample corpus of seven NLP&#8209;themed documents.",
    ])

    return f


# --------------------------------------------------------------------- CoC + security
def build_coc(styles) -> list:
    f: list = []
    f += title_block(
        styles,
        title="Code of Conduct",
        subtitle="Standards for participation in this project",
        author="Hamza Abdul Karim &middot; F23607046",
        date="May 2026",
    )
    f += abstract(
        styles,
        "This document records the standards we expect of everyone "
        "participating in the project, the scope in which they apply, "
        "and the process for reporting concerns.",
    )

    f.append(section(styles, "1", "Our Pledge"))
    f.append(body(
        styles,
        "We pledge to make participation in this project a "
        "harassment&#8209;free experience for everyone, regardless of "
        "background, identity, or level of experience.",
    ))

    f.append(section(styles, "2", "Standards"))
    f.append(body_tight(styles, "Examples of behaviour that contributes to a positive environment:"))
    f += bullet_list(styles, [
        "Using welcoming and inclusive language.",
        "Respecting differing viewpoints and experiences.",
        "Gracefully accepting constructive criticism.",
        "Focusing on what is best for the project.",
    ])
    f.append(body_tight(styles, "Examples of unacceptable behaviour:"))
    f += bullet_list(styles, [
        "Personal attacks, insulting comments, or trolling.",
        "Public or private harassment.",
        "Publishing someone's private information without consent.",
        "Other conduct which would reasonably be considered "
        "inappropriate in a professional setting.",
    ])

    f.append(section(styles, "3", "Scope"))
    f.append(body(
        styles,
        "This Code of Conduct applies within all project spaces "
        "&mdash; issues, pull requests, discussions, and any other "
        "channel maintained by the project &mdash; and also when an "
        "individual is officially representing the project in public "
        "spaces.",
    ))

    f.append(section(styles, "4", "Enforcement"))
    f.append(body(
        styles,
        "Instances of abusive, harassing, or otherwise unacceptable "
        "behaviour may be reported privately to the maintainer. All "
        "complaints will be reviewed and investigated and will result "
        "in a response that is deemed necessary and appropriate to the "
        "circumstances.",
    ))

    f.append(section(styles, "5", "Attribution"))
    f.append(body(
        styles,
        "This Code of Conduct is adapted from the Contributor Covenant, "
        "version 2.1, available at "
        "<font face='Courier'>contributor-covenant.org</font>.",
    ))
    return f


def build_security(styles) -> list:
    f: list = []
    f += title_block(
        styles,
        title="Security Policy",
        subtitle="Supported versions and disclosure process",
        author="Hamza Abdul Karim &middot; F23607046",
        date="May 2026",
    )
    f += abstract(
        styles,
        "This document describes which releases are supported with "
        "security fixes and how to report a suspected vulnerability "
        "responsibly.",
    )

    f.append(section(styles, "1", "Supported Versions"))
    f.append(body(
        styles,
        "The latest tagged release is supported with bug fixes and "
        "security patches. Older releases are not maintained.",
    ))

    f.append(section(styles, "2", "Reporting a Vulnerability"))
    f.append(body_tight(
        styles,
        "Please <b>do not</b> open a public issue for security "
        "vulnerabilities. Instead, contact the author privately so "
        "the issue can be addressed before being disclosed. When "
        "reporting, please include:",
    ))
    f += bullet_list(styles, [
        "A description of the vulnerability and its potential impact.",
        "Steps to reproduce, including a minimal proof-of-concept "
        "if possible.",
        "The affected versions or commits.",
    ])

    f.append(section(styles, "3", "Disclosure"))
    f.append(body(
        styles,
        "We follow a coordinated&#8209;disclosure model: once a fix "
        "is available we publish a release and credit the reporter "
        "(unless they wish to remain anonymous). We aim to acknowledge "
        "the report within seven days and to provide a fix or "
        "mitigation timeline once we have confirmed the issue.",
    ))
    return f
