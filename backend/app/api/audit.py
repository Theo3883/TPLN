from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models import ScoreEvent
from app.schemas.score_event import ScoreEventResponse

router = APIRouter()


@router.get("/editions/{edition_id}", response_model=list[ScoreEventResponse])
async def get_edition_audit(edition_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(ScoreEvent).where(ScoreEvent.edition_id == edition_id).order_by(ScoreEvent.created_at)
    )
    events = result.scalars().all()
    return [ScoreEventResponse.model_validate(e) for e in events]
