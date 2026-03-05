"""Internal API for crawler ingestion."""

import asyncio

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.services.crawler_runner import run_crawler_now
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models import Author, Book, Edition
from app.services.search import get_search_client
from app.core.config import settings

router = APIRouter()


def _normalize(s: str) -> str:
    if not s:
        return ""
    return " ".join(s.lower().strip().split())


class IngestItem(BaseModel):
    title: str
    authors: list[str] = []
    isbn: str | None = None
    publisher: str | None = None
    year: int | None = None


@router.post("")
async def ingest_edition(
    data: IngestItem,
    db: AsyncSession = Depends(get_db),
):
    """
    Ingest a book/edition from crawler.
    Dedup by ISBN; merge by normalized title for Book.
    """
    title = data.title.strip()
    if not title:
        raise HTTPException(status_code=400, detail="title required")

    isbn = None
    if data.isbn:
        isbn = "".join(c for c in str(data.isbn) if c.isdigit())[:17]
        if len(isbn) not in (10, 13):
            isbn = None

    normalized_title = _normalize(title)
    author_objs = []
    for name in data.authors:
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

    if isbn:
        r = await db.execute(select(Edition).where(Edition.isbn == isbn))
        existing = r.scalar_one_or_none()
        if existing:
            return {"status": "duplicate", "edition_id": existing.id}

    r = await db.execute(
        select(Book).where(Book.normalized_title == normalized_title)
    )
    book = r.scalar_one_or_none()
    if not book:
        book = Book(title=title, normalized_title=normalized_title)
        db.add(book)
        await db.flush()

    edition = Edition(
        book_id=book.id,
        isbn=isbn or None,
        publisher=data.publisher or None,
        year=data.year,
    )
    edition.authors = author_objs
    db.add(edition)
    await db.flush()
    await db.refresh(edition)

    try:
        client = get_search_client()
        index = client.index(settings.meilisearch_index)
        doc = {
            "id": edition.id,
            "title": book.title,
            "authors": " ".join(a.name for a in author_objs),
            "isbn": edition.isbn or "",
            "publisher": edition.publisher or "",
        }
        index.add_documents([doc])
    except Exception:
        pass

    return {"status": "created", "edition_id": edition.id}


@router.post("/run-crawler")
async def trigger_crawler():
    """Trigger crawler to run. Returns immediately; crawler runs in background."""
    asyncio.create_task(run_crawler_now())
    return {"status": "started", "message": "Crawler pornit. Așteaptă câteva secunde și reîmprospătează catalogul."}
