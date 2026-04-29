"""
Ingest endpoints cu rate limiting adăugat pe /run-crawler.
Modificare: Martinaș Ioana Maria — rate limiting pe trigger crawler.
"""

import asyncio

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import settings
from app.core.database import get_db
from app.core.security import limiter
from app.models import Author, Book, Edition
from app.services.crawler_runner import run_crawler_now
from app.services.search import get_search_client

router = APIRouter()


def _normalize(s: str) -> str:
    if not s:
        return ""
    return " ".join(s.lower().strip().split())


class IngestItem(BaseModel):
    """Schema de ingestie cu validare îmbunătățită."""
    title: str = Field(..., min_length=1, max_length=500, description="Titlul cărții")
    authors: list[str] = Field(default_factory=list, description="Lista de autori")
    isbn: str | None = Field(default=None, description="ISBN-10 sau ISBN-13")
    publisher: str | None = Field(default=None, max_length=255)
    year: int | None = Field(default=None, ge=1800, le=2100, description="Anul publicării")
    cover_image: str | None = Field(default=None, max_length=1024)

    @field_validator("title")
    @classmethod
    def title_not_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Titlul nu poate fi gol.")
        return v.strip()

    @field_validator("authors")
    @classmethod
    def authors_not_empty_strings(cls, v: list[str]) -> list[str]:
        return [a.strip() for a in v if a and a.strip()]


@router.post("")
async def ingest_edition(
    data: IngestItem,
    db: AsyncSession = Depends(get_db),
):
    """Ingestează o ediție din crawler. Deduplicare după ISBN și titlu normalizat."""
    title = data.title.strip()

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

    r = await db.execute(select(Book).where(Book.normalized_title == normalized_title))
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
        cover_image=data.cover_image or None,
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
@limiter.limit("5/hour")
async def trigger_crawler(request: Request):
    """
    Declanșează crawlerul manual.
    Rate limited: maxim 5 rulări/oră per IP pentru a preveni abuzul.
    """
    asyncio.create_task(run_crawler_now())
    return {
        "status": "started",
        "message": "Crawlerul a pornit în background. Reîmprospătează catalogul în câteva secunde.",
    }