"""
In-memory cache mapping ISBN and normalized title to cover image URLs.
Loaded once at startup from crawler JSON output files.
No database column required.
"""

import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
CRAWLER_OUTPUT_DIR = PROJECT_ROOT / "crawler" / "output"

# isbn (str) -> cover_url (str)
_isbn_to_cover: dict[str, str] = {}
# normalized title (str) -> cover_url (str)  (fallback when no ISBN)
_title_to_cover: dict[str, str] = {}


def _normalize(s: str) -> str:
    return " ".join(s.lower().strip().split())


def _is_valid_url(url: str) -> bool:
    return isinstance(url, str) and url.strip().startswith(("https://", "http://"))


def load_cover_cache() -> None:
    """Read all crawler JSON files and populate the cover URL caches."""
    global _isbn_to_cover, _title_to_cover
    _isbn_to_cover = {}
    _title_to_cover = {}

    if not CRAWLER_OUTPUT_DIR.exists():
        logger.warning("crawler/output/ not found, cover cache will be empty.")
        return

    for path in sorted(CRAWLER_OUTPUT_DIR.glob("*.json")):
        try:
            items = json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            logger.warning("Could not read %s: %s", path.name, exc)
            continue

        for item in items:
            if not isinstance(item, dict):
                continue
            cover = item.get("cover_image") or item.get("cover_url")
            if not _is_valid_url(cover):
                continue

            # Index by ISBN
            raw_isbn = item.get("isbn")
            if raw_isbn:
                digits = "".join(c for c in str(raw_isbn) if c.isdigit())[:17]
                if len(digits) in (10, 13):
                    _isbn_to_cover[digits] = cover

            # Index by normalized title as fallback
            title = str(item.get("title", "")).strip()
            if title:
                _title_to_cover[_normalize(title)] = cover

    logger.info(
        "Cover cache loaded: %d ISBN entries, %d title entries",
        len(_isbn_to_cover),
        len(_title_to_cover),
    )


def get_cover_url(isbn: str | None, title: str | None = None) -> str | None:
    """Look up a cover URL by ISBN, falling back to title."""
    if isbn:
        digits = "".join(c for c in str(isbn) if c.isdigit())[:17]
        result = _isbn_to_cover.get(digits)
        if result:
            return result
    if title:
        return _title_to_cover.get(_normalize(title))
    return None
