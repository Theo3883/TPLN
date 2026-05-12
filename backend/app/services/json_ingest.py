"""
Ingest crawler JSON output files into the database on startup.
Reads all *.json files from crawler/output/ and upserts editions.
"""

import json
import logging
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import async_session_maker
from app.models import Author, Book, Edition
from app.services.search import sync_edition_to_search

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
CRAWLER_OUTPUT_DIR = PROJECT_ROOT / "crawler" / "output"


def _normalize(s: str) -> str:
    if not s:
        return ""
    return " ".join(s.lower().strip().split())


async def _ingest_item(db: AsyncSession, item: dict) -> str:
    """Ingest one item. Returns 'created' or 'duplicate'."""
    title = str(item.get("title", "")).strip()
    if not title:
        return "skipped"

    raw_isbn = item.get("isbn")
    isbn = None
    if raw_isbn:
        digits = "".join(c for c in str(raw_isbn) if c.isdigit())[:17]
        if len(digits) in (10, 13):
            isbn = digits

    normalized_title = _normalize(title)

    # Dedup by ISBN — already exists, skip
    if isbn:
        r = await db.execute(select(Edition).where(Edition.isbn == isbn))
        existing = r.scalar_one_or_none()
        if existing:
            return "duplicate"

    # Authors
    author_objs: list[Author] = []
    for name in item.get("authors", []):
        if not name or not str(name).strip():
            continue
        n = str(name).strip()
        norm = _normalize(n)
        r = await db.execute(select(Author).where(Author.normalized_name == norm))
        a = r.scalar_one_or_none()
        if not a:
            a = Author(name=n, normalized_name=norm)
            db.add(a)
            await db.flush()
        author_objs.append(a)

    # Book (dedup by normalized title)
    r = await db.execute(select(Book).where(Book.normalized_title == normalized_title))
    book = r.scalar_one_or_none()
    if not book:
        book = Book(title=title, normalized_title=normalized_title)
        db.add(book)
        await db.flush()

    # Edition
    edition = Edition(
        book_id=book.id,
        isbn=isbn,
        publisher=item.get("publisher") or None,
        year=item.get("year") or None,
    )
    edition.authors = author_objs
    db.add(edition)
    await db.flush()
    await db.refresh(edition)

    try:
        await sync_edition_to_search(edition, book, author_objs)
    except Exception:
        pass

    return "created"


async def ingest_from_crawler_output() -> None:
    """Read all JSON files from crawler/output/ and ingest into the DB."""
    if not CRAWLER_OUTPUT_DIR.exists():
        logger.warning("crawler/output/ not found, skipping startup ingest.")
        return

    json_files = sorted(CRAWLER_OUTPUT_DIR.glob("*.json"))
    if not json_files:
        logger.info("No crawler JSON files found, skipping startup ingest.")
        return

    total = inserted = duplicates = skipped = 0

    async with async_session_maker() as db:
        for path in json_files:
            try:
                items = json.loads(path.read_text(encoding="utf-8"))
            except Exception as e:
                logger.warning("Could not read %s: %s", path.name, e)
                continue

            for item in items:
                total += 1
                try:
                    status = await _ingest_item(db, item)
                    if status == "created":
                        inserted += 1
                    elif status == "duplicate":
                        duplicates += 1
                    else:
                        skipped += 1
                except Exception as e:
                    logger.error("Error ingesting item '%s': %s", item.get("title"), e)
                    await db.rollback()
                    skipped += 1

        await db.commit()

    logger.info(
        "Startup ingest complete — total=%d inserted=%d duplicates=%d skipped=%d",
        total, inserted, duplicates, skipped,
    )
