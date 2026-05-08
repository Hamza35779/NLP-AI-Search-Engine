"""Generate every PDF article in the project.

Run from the repository root:

    python scripts/build_docs.py
"""

from __future__ import annotations

import os
import sys

# Make the repo root importable so `scripts.*` works when running directly.
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from scripts._pdf_doc import write_pdf  # noqa: E402
from scripts._pdf_styles import build_styles  # noqa: E402
from scripts.articles import (  # noqa: E402
    api as art_api,
    architecture as art_arch,
    development as art_dev,
    meta as art_meta,
    ranking as art_rank,
    readme as art_readme,
)


AUTHOR = "Hamza Abdul Karim"
FOOTER = "NLP Search Engine"


def main() -> int:
    styles = build_styles()
    os.makedirs(os.path.join(ROOT, "docs"), exist_ok=True)

    targets = [
        # (relative_path, title,                   builder)
        ("docs/architecture.pdf",
         "System Architecture of an NLP Search Engine",
         art_arch.build),
        ("docs/ranking-models.pdf",
         "Sparse Ranking Models",
         art_rank.build),
        ("docs/api.pdf",
         "HTTP API Reference",
         art_api.build),
        ("docs/development.pdf",
         "Development Guide",
         art_dev.build),
        ("README.pdf",
         "NLP Search Engine — README",
         art_readme.build),
        ("CONTRIBUTING.pdf",
         "Contributing Guide",
         art_meta.build_contributing),
        ("CHANGELOG.pdf",
         "Release History",
         art_meta.build_changelog),
        ("CODE_OF_CONDUCT.pdf",
         "Code of Conduct",
         art_meta.build_coc),
        ("SECURITY.pdf",
         "Security Policy",
         art_meta.build_security),
    ]

    for rel_path, title, builder in targets:
        out = os.path.join(ROOT, rel_path)
        os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
        flowables = builder(styles)
        write_pdf(out, flowables, title=title, author=AUTHOR, footer=FOOTER)
        print(f"  wrote {rel_path}")

    print(f"\nGenerated {len(targets)} PDF documents.")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
