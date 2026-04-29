from __future__ import annotations

import html


def safe(value: str) -> str:
    return html.escape(str(value))


def cover_markup(letter: str, rounded_top: bool = False, image_url: str | None = None) -> str:
    style = ""
    if rounded_top:
        style = "border-top-left-radius:180px;border-top-right-radius:180px;"
    if image_url:
        return f"<div class='cover' style='padding:0;overflow:hidden;{style}'><img src='{safe(image_url)}' alt='{safe(letter)}' style='width:100%;height:100%;object-fit:cover;display:block;' referrerpolicy='no-referrer' /></div>"
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
