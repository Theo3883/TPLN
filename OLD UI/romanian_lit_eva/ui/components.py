from __future__ import annotations

import html


def safe(value: str) -> str:
    return html.escape(str(value))


def cover_markup(letter: str, rounded_top: bool = False) -> str:
    style = ""
    if rounded_top:
        style = "border-top-left-radius:180px;border-top-right-radius:180px;"
    return f"<div class='cover' style='{style}'>{safe(letter)}</div>"


def confidence_markup(confidence: float) -> str:
    width = max(0, min(100, int(confidence * 100)))
    return (
        "<div class='metric-wrap'>"
        f"<div class='metric-bar'><span style='width:{width}%'></span></div>"
        f"<div class='mono muted' style='font-size:.68rem;'>{confidence:.2f}</div>"
        "</div>"
    )


def section_header_markup(title: str, subtitle: str) -> str:
    return (
        f"<h1 class='section-title'>{safe(title)}</h1>"
        f"<div class='section-sub'>{safe(subtitle)}</div>"
    )
