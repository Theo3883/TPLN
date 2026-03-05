from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models import Review
from app.schemas.review import ReviewResponse

router = APIRouter()


@router.get("/pending", response_model=list[ReviewResponse])
async def list_pending_reviews(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Review).where(Review.status == "pending").order_by(Review.created_at)
    )
    return [ReviewResponse.model_validate(r) for r in result.scalars().all()]


@router.post("/{review_id}/approve")
async def approve_review(review_id: int, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(Review).where(Review.id == review_id))
    review = r.scalar_one_or_none()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    review.status = "approved"
    return {"status": "approved"}


@router.post("/{review_id}/reject")
async def reject_review(review_id: int, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(Review).where(Review.id == review_id))
    review = r.scalar_one_or_none()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    review.status = "rejected"
    return {"status": "rejected"}
