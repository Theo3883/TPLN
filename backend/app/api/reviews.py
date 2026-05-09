from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.config import settings
from app.core.security import get_current_user, limiter
from app.models import Edition, Review, Reviewer, User
from app.schemas.review import ReviewCreate, ReviewResponse

router = APIRouter()
create_router = APIRouter()


@router.get("/{edition_id}/reviews", response_model=list[ReviewResponse])
async def list_reviews(
    edition_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Review).where(Review.edition_id == edition_id).offset(skip).limit(limit)
    )
    reviews = result.scalars().all()
    return [ReviewResponse.model_validate(r) for r in reviews]


@create_router.post(
    "/reviews",
    response_model=ReviewResponse,
)
@limiter.limit(f"{settings.rate_limit_reviews_per_hour}/hour")
async def create_review(
    request: Request,
    review_in: ReviewCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new review (requires authentication).
    Uses the authenticated user's associated reviewer.
    """
    edition_result = await db.execute(select(Edition).where(Edition.id == review_in.edition_id))
    if not edition_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Edition not found")

    # Get or create reviewer for the authenticated user
    reviewer_result = await db.execute(
        select(Reviewer).where(Reviewer.user_id == current_user.id)
    )
    reviewer = reviewer_result.scalar_one_or_none()
    
    if not reviewer:
        # This shouldn't happen as reviewer is created during registration,
        # but handle it just in case
        reviewer = Reviewer(
            identifier=current_user.email,
            user_id=current_user.id,
            migrated=True
        )
        db.add(reviewer)
        await db.flush()

    review = Review(
        edition_id=review_in.edition_id,
        reviewer_id=reviewer.id,
        content=review_in.content,
        rating=review_in.rating,
    )
    db.add(review)
    await db.flush()

    from app.services.scoring import compute_score
    from app.models import ScoreEvent

    edition = edition_result.scalar_one_or_none()
    ratings_result = await db.execute(
        select(Review.rating).where(
            Review.edition_id == review_in.edition_id,
            Review.rating.isnot(None),
            Review.status.in_(["approved", "pending"]),
        )
    )
    ratings = [row[0] for row in ratings_result.all()]

    old_score = edition.score
    new_score, confidence = compute_score(ratings)
    edition.score = new_score
    edition.confidence = confidence
    edition.review_count = len(ratings)

    score_event = ScoreEvent(
        edition_id=review_in.edition_id,
        old_score=old_score,
        new_score=new_score,
        reason="new_review",
    )
    db.add(score_event)
    await db.refresh(review)
    return ReviewResponse.model_validate(review)
