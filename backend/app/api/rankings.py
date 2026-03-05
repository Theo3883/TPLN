from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models import Edition
from app.schemas.ranking import RankingItem

router = APIRouter()


@router.get("", response_model=list[RankingItem])
async def get_rankings(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Edition)
        .options(selectinload(Edition.book), selectinload(Edition.authors))
        .where(Edition.score.isnot(None))
        .order_by(desc(Edition.score))
        .offset(skip)
        .limit(limit)
    )
    editions = result.scalars().all()
    return [
        RankingItem(
            edition_id=e.id,
            title=e.book.title if e.book else "",
            authors=[a.name for a in e.authors],
            score=e.score or 0,
            confidence=e.confidence or 0,
            review_count=e.review_count,
        )
        for e in editions
    ]
