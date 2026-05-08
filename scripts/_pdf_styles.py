"""Black-and-white academic-article styles for ReportLab.

A small set of paragraph styles, numbered-section helpers, and page
template configuration shared by every PDF in `scripts/build_docs.py`.
"""

from __future__ import annotations

from reportlab.lib.colors import black, white, HexColor
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm

PAGE_SIZE = A4
LEFT_MARGIN = 2.4 * cm
RIGHT_MARGIN = 2.4 * cm
TOP_MARGIN = 2.0 * cm
BOTTOM_MARGIN = 2.4 * cm

BODY_FONT = "Times-Roman"
BODY_BOLD = "Times-Bold"
BODY_ITAL = "Times-Italic"
MONO_FONT = "Courier"

CODE_BG = HexColor("#f0f0f0")
RULE_GRAY = HexColor("#999999")


def build_styles() -> dict[str, ParagraphStyle]:
    """Return a dictionary of named paragraph styles."""
    base = getSampleStyleSheet()["Normal"]
    styles: dict[str, ParagraphStyle] = {}

    styles["Title"] = ParagraphStyle(
        "Title", parent=base, fontName=BODY_BOLD,
        fontSize=20, leading=24, alignment=TA_CENTER,
        spaceAfter=4, textColor=black,
    )
    styles["Subtitle"] = ParagraphStyle(
        "Subtitle", parent=base, fontName=BODY_ITAL,
        fontSize=12, leading=15, alignment=TA_CENTER,
        spaceAfter=6, textColor=black,
    )
    styles["Author"] = ParagraphStyle(
        "Author", parent=base, fontName=BODY_FONT,
        fontSize=11, leading=14, alignment=TA_CENTER,
        spaceAfter=18, textColor=black,
    )
    styles["Abstract"] = ParagraphStyle(
        "Abstract", parent=base, fontName=BODY_ITAL,
        fontSize=10.5, leading=13.5, alignment=TA_JUSTIFY,
        leftIndent=1.0 * cm, rightIndent=1.0 * cm,
        spaceBefore=4, spaceAfter=14,
    )
    styles["AbstractHead"] = ParagraphStyle(
        "AbstractHead", parent=base, fontName=BODY_BOLD,
        fontSize=10.5, leading=13.5, alignment=TA_CENTER,
        leftIndent=1.0 * cm, rightIndent=1.0 * cm,
        spaceAfter=2,
    )
    styles["H1"] = ParagraphStyle(
        "H1", parent=base, fontName=BODY_BOLD,
        fontSize=14, leading=18, alignment=TA_LEFT,
        spaceBefore=14, spaceAfter=6, keepWithNext=True,
    )
    styles["H2"] = ParagraphStyle(
        "H2", parent=base, fontName=BODY_BOLD,
        fontSize=12, leading=16, alignment=TA_LEFT,
        spaceBefore=10, spaceAfter=4, keepWithNext=True,
    )
    styles["H3"] = ParagraphStyle(
        "H3", parent=base, fontName=BODY_ITAL,
        fontSize=11, leading=14, alignment=TA_LEFT,
        spaceBefore=8, spaceAfter=2, keepWithNext=True,
    )
    styles["Body"] = ParagraphStyle(
        "Body", parent=base, fontName=BODY_FONT,
        fontSize=10.5, leading=14, alignment=TA_JUSTIFY,
        firstLineIndent=14, spaceAfter=4,
    )
    styles["BodyTight"] = ParagraphStyle(
        "BodyTight", parent=styles["Body"], firstLineIndent=0,
        spaceAfter=2,
    )
    styles["Bullet"] = ParagraphStyle(
        "Bullet", parent=base, fontName=BODY_FONT,
        fontSize=10.5, leading=13.5, alignment=TA_LEFT,
        leftIndent=22, bulletIndent=8, spaceAfter=2,
    )
    styles["FigureCaption"] = ParagraphStyle(
        "FigureCaption", parent=base, fontName=BODY_FONT,
        fontSize=9.5, leading=12, alignment=TA_CENTER,
        spaceBefore=4, spaceAfter=12, textColor=black,
    )
    styles["EquationLabel"] = ParagraphStyle(
        "EquationLabel", parent=base, fontName=BODY_FONT,
        fontSize=9.5, leading=12, alignment=TA_CENTER,
        spaceBefore=2, spaceAfter=10, textColor=black,
    )
    styles["Code"] = ParagraphStyle(
        "Code", parent=base, fontName=MONO_FONT,
        fontSize=9, leading=12, alignment=TA_LEFT,
        leftIndent=10, rightIndent=10,
        backColor=CODE_BG, borderPadding=6,
        spaceBefore=4, spaceAfter=8,
    )
    styles["TableCell"] = ParagraphStyle(
        "TableCell", parent=base, fontName=BODY_FONT,
        fontSize=9.5, leading=12, alignment=TA_LEFT,
    )
    styles["TableHead"] = ParagraphStyle(
        "TableHead", parent=base, fontName=BODY_BOLD,
        fontSize=9.5, leading=12, alignment=TA_LEFT,
    )
    return styles


def page_decorations(canvas, doc, *, footer_text: str) -> None:
    """Draw a thin rule and a centered page-number footer."""
    canvas.saveState()
    canvas.setStrokeColor(RULE_GRAY)
    canvas.setLineWidth(0.4)
    canvas.line(
        LEFT_MARGIN,
        BOTTOM_MARGIN - 0.6 * cm,
        PAGE_SIZE[0] - RIGHT_MARGIN,
        BOTTOM_MARGIN - 0.6 * cm,
    )
    canvas.setFont(BODY_FONT, 9)
    canvas.setFillColor(black)
    canvas.drawCentredString(
        PAGE_SIZE[0] / 2,
        BOTTOM_MARGIN - 1.1 * cm,
        f"{footer_text}   |   page {doc.page}",
    )
    canvas.restoreState()
