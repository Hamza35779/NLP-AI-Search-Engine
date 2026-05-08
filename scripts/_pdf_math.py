"""Render LaTeX-style math equations into ReportLab Image flowables.

Uses matplotlib's ``mathtext`` (no external LaTeX required) so the
equations look like they came from a typeset article.
"""

from __future__ import annotations

import os
from io import BytesIO
from typing import Optional

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402  (matplotlib backend selected first)
from reportlab.lib.units import cm  # noqa: E402
from reportlab.platypus import Image  # noqa: E402


_DPI = 240


def render_math(latex: str, *, fontsize: int = 16, padding: float = 0.18) -> BytesIO:
    """Render a single math expression to an in-memory PNG buffer."""
    fig = plt.figure(figsize=(0.01, 0.01))
    fig.patch.set_alpha(0.0)
    text = fig.text(
        0, 0,
        f"${latex}$",
        fontsize=fontsize,
        color="black",
    )

    fig.canvas.draw()
    bbox = text.get_window_extent()
    width_in = bbox.width / _DPI + 2 * padding
    height_in = bbox.height / _DPI + 2 * padding
    fig.set_size_inches(width_in, height_in)
    text.set_position((padding / width_in, padding / height_in))

    buf = BytesIO()
    fig.savefig(
        buf, format="png", dpi=_DPI,
        bbox_inches="tight", pad_inches=0.04,
        transparent=True,
    )
    plt.close(fig)
    buf.seek(0)
    return buf


def equation(
    latex: str,
    *,
    width_cm: Optional[float] = None,
    fontsize: int = 16,
) -> Image:
    """Return a centered Image flowable for the given LaTeX expression."""
    buf = render_math(latex, fontsize=fontsize)
    img = Image(buf)
    # Sniff the natural pixel dimensions and convert to cm at 96 dpi.
    natural_w = img.imageWidth / _DPI * 2.54
    natural_h = img.imageHeight / _DPI * 2.54
    if width_cm and natural_w > width_cm:
        scale = width_cm / natural_w
        natural_w *= scale
        natural_h *= scale
    img.drawWidth = natural_w * cm
    img.drawHeight = natural_h * cm
    img.hAlign = "CENTER"
    return img


def save_math_png(latex: str, path: str, *, fontsize: int = 16) -> str:
    """Render math to a file (used for diagrams that ship as raw assets)."""
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    buf = render_math(latex, fontsize=fontsize)
    with open(path, "wb") as fh:
        fh.write(buf.getvalue())
    return path
