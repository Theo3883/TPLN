from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models import Edition
from app.schemas.edition import EditionResponse, AuthorSchema, BookSchema

router = APIRouter()


@router.get("", response_model=list[EditionResponse])
async def list_editions(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Edition)
        .options(selectinload(Edition.book), selectinload(Edition.authors))
        .offset(skip)
        .limit(limit)
    )
    editions = result.scalars().all()
    return [
        EditionResponse(
            id=e.id,
            book_id=e.book_id,
            isbn=e.isbn,
            publisher=e.publisher,
            year=e.year,
            score=e.score,
            confidence=e.confidence,
            review_count=e.review_count,
            book=BookSchema(id=e.book.id, title=e.book.title) if e.book else None,
            authors=[AuthorSchema(id=a.id, name=a.name) for a in e.authors],
        )
        for e in editions
    ]


@router.get("/{edition_id}", response_model=EditionResponse)
async def get_edition(edition_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Edition)
        .options(selectinload(Edition.book), selectinload(Edition.authors))
        .where(Edition.id == edition_id)
    )
    e = result.scalar_one_or_none()
    if not e:
        raise HTTPException(status_code=404, detail="Edition not found")
    return EditionResponse(
        id=e.id,
        book_id=e.book_id,
        isbn=e.isbn,
        publisher=e.publisher,
        year=e.year,
        score=e.score,
        confidence=e.confidence,
        review_count=e.review_count,
        book=BookSchema(id=e.book.id, title=e.book.title) if e.book else None,
        authors=[AuthorSchema(id=a.id, name=a.name) for a in e.authors],
    )
