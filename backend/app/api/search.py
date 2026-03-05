from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models import Edition
from app.schemas.edition import EditionResponse, AuthorSchema, BookSchema
from app.services.search import get_search_client
from app.core.config import settings

router = APIRouter()


@router.get("/search/editions", response_model=list[EditionResponse])
async def search_editions(
    q: str = Query(..., min_length=1),
    db: AsyncSession = Depends(get_db),
):
    client = get_search_client()
    index = client.index(settings.meilisearch_index)
    result = index.search(q, {"limit": 20})
    hits = result.get("hits", [])
    if not hits:
        return []

    ids = [h["id"] for h in hits]
    db_result = await db.execute(
        select(Edition)
        .options(selectinload(Edition.book), selectinload(Edition.authors))
        .where(Edition.id.in_(ids))
    )
    editions = {e.id: e for e in db_result.scalars().all()}
    ordered = [editions[i] for i in ids if i in editions]
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
        for e in ordered
    ]
