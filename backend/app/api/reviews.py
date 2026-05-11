from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.core.database import get_db
from app.core.config import settings
from app.core.security import get_current_user, get_current_user_optional, limiter
from app.models import Edition, Review, Reviewer, User, ReviewLike
from app.schemas.review import ReviewCreate, ReviewResponse, SentimentLabel
from app.services.sentiment_analyzer import analyze_review_sentiment

router = APIRouter()
create_router = APIRouter()


@router.get("/{edition_id}/reviews", response_model=list[ReviewResponse])
async def list_reviews(
    edition_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Review).where(Review.edition_id == edition_id).offset(skip).limit(limit)
    )
    reviews = result.scalars().all()
    
    # Build response with liked_by_user field
    response = []
    for review in reviews:
        review_dict = ReviewResponse.model_validate(review).model_dump()
        
        # Check if current user has liked this review
        if current_user:
            like_result = await db.execute(
                select(ReviewLike).where(
                    ReviewLike.review_id == review.id,
                    ReviewLike.user_id == current_user.id
                )
            )
            review_dict["liked_by_user"] = like_result.scalar_one_or_none() is not None
        else:
            review_dict["liked_by_user"] = False
        
        response.append(ReviewResponse(**review_dict))
    
    return response


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
    Automatically analyzes sentiment using NLP.
    """
    # Fetch edition
    edition_result = await db.execute(select(Edition).where(Edition.id == review_in.edition_id))
    edition = edition_result.scalar_one_or_none()
    
    if not edition:
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

    # ANALYZE SENTIMENT AUTOMATICALLY
    sentiment = await analyze_review_sentiment(review_in.content)

    review = Review(
        edition_id=review_in.edition_id,
        reviewer_id=reviewer.id,
        content=review_in.content,
        rating=review_in.rating,
        sentiment_label=sentiment["label"],
        sentiment_score=sentiment["score"],
        sentiment_confidence=sentiment["confidence"],
    )
    db.add(review)
    await db.flush()

    from app.services.scoring import compute_score
    from app.models import ScoreEvent

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
