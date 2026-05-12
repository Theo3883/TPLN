from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models import Edition
from app.schemas.edition import EditionResponse, AuthorSchema, BookSchema, EditionSource, CrawlerName
from app.services.cover_cache import get_cover_url

router = APIRouter()


def _resolve_cover(e: Edition) -> str | None:
    """Get cover URL: prefer DB column (if migration ran), fall back to cache."""
    db_val = getattr(e, "cover_url", None)
    if db_val:
        return db_val
    title = e.book.title if e.book else None
    return get_cover_url(e.isbn, title)


@router.get("", response_model=list[EditionResponse])
async def list_editions(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    source: EditionSource | None = Query(None, description="Filter by source: manual or crawler"),
    crawler_name: CrawlerName | None = Query(None, description="Filter by specific crawler"),
    db: AsyncSession = Depends(get_db),
):
    """
    List editions with optional filtering by source and crawler.
    
    - **source**: Filter by 'manual' or 'crawler' entries
    - **crawler_name**: Filter by specific crawler (bookzone, carturesti, libris)
    - **skip**: Number of records to skip for pagination
    - **limit**: Maximum number of records to return
    """
    query = select(Edition).options(
        selectinload(Edition.book),
        selectinload(Edition.authors)
    )
    
    # Apply source filter
    if source:
        query = query.where(Edition.source == source.value)
    
    # Apply crawler_name filter
    if crawler_name:
        query = query.where(Edition.crawler_name == crawler_name.value)
    
    # Apply pagination
    query = query.offset(skip).limit(limit)
    
    result = await db.execute(query)
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
            source=EditionSource(e.source),
            crawler_name=CrawlerName(e.crawler_name) if e.crawler_name else None,
            imported_at=e.imported_at,
            cover_url=_resolve_cover(e),
            book=BookSchema(id=e.book.id, title=e.book.title) if e.book else None,
            authors=[AuthorSchema(id=a.id, name=a.name) for a in e.authors],
        )
        for e in editions
    ]


@router.get("/{edition_id}", response_model=EditionResponse)
async def get_edition(edition_id: int, db: AsyncSession = Depends(get_db)):
    """Get a single edition by ID with all related data."""
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
        source=EditionSource(e.source),
        crawler_name=CrawlerName(e.crawler_name) if e.crawler_name else None,
        imported_at=e.imported_at,
        cover_url=_resolve_cover(e),
        book=BookSchema(id=e.book.id, title=e.book.title) if e.book else None,
        authors=[AuthorSchema(id=a.id, name=a.name) for a in e.authors],
    )


@router.get("", response_model=list[EditionResponse])
async def list_editions(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    source: EditionSource | None = Query(None, description="Filter by source: manual or crawler"),
    crawler_name: CrawlerName | None = Query(None, description="Filter by specific crawler"),
    db: AsyncSession = Depends(get_db),
):
    """
    List editions with optional filtering by source and crawler.
    
    - **source**: Filter by 'manual' or 'crawler' entries
    - **crawler_name**: Filter by specific crawler (bookzone, carturesti, libris)
    - **skip**: Number of records to skip for pagination
    - **limit**: Maximum number of records to return
    """
    query = select(Edition).options(
        selectinload(Edition.book),
        selectinload(Edition.authors)
    )
    
    # Apply source filter
    if source:
        query = query.where(Edition.source == source.value)
    
    # Apply crawler_name filter
    if crawler_name:
        query = query.where(Edition.crawler_name == crawler_name.value)
    
    # Apply pagination
    query = query.offset(skip).limit(limit)
    
    result = await db.execute(query)
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
            source=EditionSource(e.source),
            crawler_name=CrawlerName(e.crawler_name) if e.crawler_name else None,
            imported_at=e.imported_at,
            cover_url=e.cover_url,
            book=BookSchema(id=e.book.id, title=e.book.title) if e.book else None,
            authors=[AuthorSchema(id=a.id, name=a.name) for a in e.authors],
        )
        for e in editions
    ]


@router.get("/{edition_id}", response_model=EditionResponse)
async def get_edition(edition_id: int, db: AsyncSession = Depends(get_db)):
    """Get a single edition by ID with all related data."""
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
        source=EditionSource(e.source),
        crawler_name=CrawlerName(e.crawler_name) if e.crawler_name else None,
        imported_at=e.imported_at,
        cover_url=e.cover_url,
        book=BookSchema(id=e.book.id, title=e.book.title) if e.book else None,
        authors=[AuthorSchema(id=a.id, name=a.name) for a in e.authors],
    )
