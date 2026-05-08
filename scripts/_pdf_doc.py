"""Build a single PDF from a list of flowables in academic style."""

from __future__ import annotations

from functools import partial
from typing import Iterable

from reportlab.platypus import BaseDocTemplate, Frame, PageTemplate

from ._pdf_styles import (  # type: ignore[import-not-found]
    BOTTOM_MARGIN, LEFT_MARGIN, PAGE_SIZE,
    RIGHT_MARGIN, TOP_MARGIN, page_decorations,
)


def write_pdf(
    path: str,
    flowables: Iterable,
    *,
    title: str,
    author: str,
    footer: str,
) -> str:
    """Render `flowables` to `path` with the standard page template."""
    doc = BaseDocTemplate(
        path,
        pagesize=PAGE_SIZE,
        leftMargin=LEFT_MARGIN,
        rightMargin=RIGHT_MARGIN,
        topMargin=TOP_MARGIN,
        bottomMargin=BOTTOM_MARGIN,
        title=title,
        author=author,
    )
    frame = Frame(
        doc.leftMargin,
        doc.bottomMargin,
        doc.width,
        doc.height,
        id="content",
        showBoundary=0,
    )
    template = PageTemplate(
        id="article",
        frames=[frame],
        onPage=partial(page_decorations, footer_text=footer),
    )
    doc.addPageTemplates([template])
    doc.build(list(flowables))
    return path
