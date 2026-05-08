"""Reusable flowable factories: figures, code, tables, equations.

Combined with `_pdf_styles` and `_pdf_math` these give every PDF in the
project a consistent academic look.
"""

from __future__ import annotations

import html
from typing import Iterable, Optional, Sequence

from reportlab.lib.units import cm
from reportlab.platypus import (
    KeepTogether, Paragraph, Spacer, Table, TableStyle,
)
from svglib.svglib import svg2rlg

from ._pdf_math import equation as math_image  # type: ignore[import-not-found]


def title_block(styles, title: str, subtitle: str, author: str, date: str) -> list:
    return [
        Paragraph(title, styles["Title"]),
        Paragraph(subtitle, styles["Subtitle"]),
        Paragraph(f"{author} &mdash; {date}", styles["Author"]),
    ]


def abstract(styles, text: str) -> list:
    return [
        Paragraph("ABSTRACT", styles["AbstractHead"]),
        Paragraph(text, styles["Abstract"]),
    ]


def section(styles, num: str, title: str) -> Paragraph:
    return Paragraph(f"{num}.&nbsp;&nbsp;{title}", styles["H1"])


def subsection(styles, num: str, title: str) -> Paragraph:
    return Paragraph(f"{num}&nbsp;&nbsp;{title}", styles["H2"])


def body(styles, text: str) -> Paragraph:
    return Paragraph(text, styles["Body"])


def body_tight(styles, text: str) -> Paragraph:
    return Paragraph(text, styles["BodyTight"])


def bullet_list(styles, items: Iterable[str]) -> list:
    flowables: list = []
    for item in items:
        flowables.append(
            Paragraph(item, styles["Bullet"], bulletText="•")
        )
    return flowables


def code_block(styles, lines: Iterable[str]) -> Paragraph:
    """A simple monospace block. Newlines preserved via <br/>."""
    safe = [html.escape(line) for line in lines]
    return Paragraph("<br/>".join(safe), styles["Code"])


def figure(
    styles,
    svg_path: str,
    caption: str,
    *,
    max_width_cm: float = 16.0,
) -> KeepTogether:
    """Embed an SVG and add a centered caption beneath it."""
    drawing = svg2rlg(svg_path)
    if drawing is None:
        raise FileNotFoundError(svg_path)

    natural_w = drawing.width
    natural_h = drawing.height
    target_pts = max_width_cm * cm
    if natural_w > target_pts:
        scale = target_pts / natural_w
        drawing.width = natural_w * scale
        drawing.height = natural_h * scale
        drawing.scale(scale, scale)
    drawing.hAlign = "CENTER"
    return KeepTogether(
        [drawing, Spacer(1, 0.05 * cm), Paragraph(caption, styles["FigureCaption"])]
    )


def equation_block(
    styles, latex: str, label: Optional[str] = None,
) -> KeepTogether:
    parts: list = [Spacer(1, 0.05 * cm), math_image(latex, width_cm=15.0)]
    if label:
        parts.append(Paragraph(label, styles["EquationLabel"]))
    return KeepTogether(parts)


def styled_table(
    styles,
    header: Sequence[str],
    rows: Sequence[Sequence[str]],
    *,
    col_widths: Optional[Sequence[float]] = None,
) -> Table:
    data = [
        [Paragraph(html.escape(cell), styles["TableHead"]) for cell in header]
    ] + [
        [Paragraph(html.escape(cell), styles["TableCell"]) for cell in row]
        for row in rows
    ]

    if col_widths is None:
        col_widths = [16.0 / len(header) * cm for _ in header]

    table = Table(data, colWidths=list(col_widths), repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (-1, 0), "Times-Bold"),
                ("LINEBELOW", (0, 0), (-1, 0), 0.6, (0, 0, 0)),
                ("LINEBELOW", (0, -1), (-1, -1), 0.4, (0.6, 0.6, 0.6)),
                ("LINEABOVE", (0, 0), (-1, 0), 0.6, (0, 0, 0)),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    return table


def small_gap(height_cm: float = 0.15) -> Spacer:
    return Spacer(1, height_cm * cm)
