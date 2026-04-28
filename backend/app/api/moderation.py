"""
Moderation endpoints cu rate limiting adăugat.
Modificare: Martinaș Ioana Maria — adăugat rate limiting pe approve/reject.
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import limiter
from app.models import Review
from app.schemas.review import ReviewResponse

router = APIRouter()


@router.get("/pending", response_model=list[ReviewResponse])
async def list_pending_reviews(db: AsyncSession = Depends(get_db)):
    """Listează toate recenziile în așteptarea moderării."""
    result = await db.execute(
        select(Review).where(Review.status == "pending").order_by(Review.created_at)
    )
    return [ReviewResponse.model_validate(r) for r in result.scalars().all()]


@router.post("/{review_id}/approve")
@limiter.limit("60/hour")
async def approve_review(
    request: Request,
    review_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Aprobă o recenzie. Rate limited: maxim 60 aprobări/oră per IP."""
    r = await db.execute(select(Review).where(Review.id == review_id))
    review = r.scalar_one_or_none()
    if not review:
        raise HTTPException(status_code=404, detail=f"Recenzia cu id={review_id} nu există.")
    if review.status != "pending":
        raise HTTPException(
            status_code=409,
            detail=f"Recenzia are statusul '{review.status}', nu poate fi aprobată din nou.",
        )
    review.status = "approved"
    return {"status": "approved", "review_id": review_id}


@router.post("/{review_id}/reject")
@limiter.limit("60/hour")
async def reject_review(
    request: Request,
    review_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Respinge o recenzie. Rate limited: maxim 60 respingeri/oră per IP."""
    r = await db.execute(select(Review).where(Review.id == review_id))
    review = r.scalar_one_or_none()
    if not review:
        raise HTTPException(status_code=404, detail=f"Recenzia cu id={review_id} nu există.")
    if review.status != "pending":
        raise HTTPException(
            status_code=409,
            detail=f"Recenzia are statusul '{review.status}', nu poate fi respinsă din nou.",
        )
    review.status = "rejected"
    return {"status": "rejected", "review_id": review_id}