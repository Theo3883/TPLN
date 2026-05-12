"""
API endpoints for review likes and book unlocks.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models import Review, ReviewLike, User, Edition, UnlockedBook, Reviewer
from app.services.unlock_service import (
    check_and_update_unlocks,
    get_top_review_for_edition,
    is_edition_unlocked_for_user,
    get_user_unlocked_editions
)

router = APIRouter()


@router.post("/reviews/{review_id}/like", status_code=status.HTTP_200_OK)
async def like_review(
    review_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Like a review. If already liked, returns 200 (idempotent).
    Automatically recalculates top review and unlocks for the edition.
    """
    # Check if review exists
    review_result = await db.execute(select(Review).where(Review.id == review_id))
    review = review_result.scalar_one_or_none()
    
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    
    # Check if user is trying to like their own review
    reviewer_result = await db.execute(
        select(Reviewer).where(Reviewer.id == review.reviewer_id)
    )
    reviewer = reviewer_result.scalar_one_or_none()
    if reviewer and reviewer.user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot like your own review")
    
    # Check if already liked
    existing_like = await db.execute(
        select(ReviewLike).where(
            and_(
                ReviewLike.review_id == review_id,
                ReviewLike.user_id == current_user.id
            )
        )
    )
    if existing_like.scalar_one_or_none():
        return {"message": "Already liked", "like_count": review.like_count}
    
    # Create like
    like = ReviewLike(review_id=review_id, user_id=current_user.id)
    db.add(like)
    
    # Update like count
    review.like_count += 1
    await db.flush()
    
    # Recalculate unlocks for this edition
    unlock_result = await check_and_update_unlocks(db, review.edition_id)
    
    await db.commit()
    await db.refresh(review)
    
    return {
        "message": "Review liked",
        "like_count": review.like_count,
        "unlocked_user_id": unlock_result.get("unlocked_user_id"),
        "locked_user_ids": unlock_result.get("locked_user_ids")
    }


@router.delete("/reviews/{review_id}/like", status_code=status.HTTP_200_OK)
async def unlike_review(
    review_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Unlike a review. If not liked, returns 200 (idempotent).
    Automatically recalculates top review and unlocks for the edition.
    """
    # Check if review exists
    review_result = await db.execute(select(Review).where(Review.id == review_id))
    review = review_result.scalar_one_or_none()
    
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    
    # Find existing like
    like_result = await db.execute(
        select(ReviewLike).where(
            and_(
                ReviewLike.review_id == review_id,
                ReviewLike.user_id == current_user.id
            )
        )
    )
    like = like_result.scalar_one_or_none()
    
    if not like:
        return {"message": "Not liked", "like_count": review.like_count}
    
    # Delete like
    await db.delete(like)
    
    # Update like count
    review.like_count = max(0, review.like_count - 1)
    await db.flush()
    
    # Recalculate unlocks for this edition
    unlock_result = await check_and_update_unlocks(db, review.edition_id)
    
    await db.commit()
    await db.refresh(review)
    
    return {
        "message": "Review unliked",
        "like_count": review.like_count,
        "unlocked_user_id": unlock_result.get("unlocked_user_id"),
        "locked_user_ids": unlock_result.get("locked_user_ids")
    }


@router.get("/editions/{edition_id}/top-review")
async def get_edition_top_review(
    edition_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get the review with the most likes for an edition."""
    top_review = await get_top_review_for_edition(db, edition_id)
    
    if not top_review:
        return None
    
    # Get reviewer info
    reviewer_result = await db.execute(
        select(Reviewer).where(Reviewer.id == top_review.reviewer_id)
    )
    reviewer = reviewer_result.scalar_one_or_none()
    
    return {
        "id": top_review.id,
        "content": top_review.content,
        "rating": top_review.rating,
        "like_count": top_review.like_count,
        "sentiment_label": top_review.sentiment_label,
        "sentiment_score": top_review.sentiment_score,
        "sentiment_confidence": top_review.sentiment_confidence,
        "created_at": top_review.created_at,
        "reviewer_name": reviewer.identifier if reviewer else "Unknown"
    }


@router.get("/editions/{edition_id}/is-unlocked")
async def check_edition_unlocked(
    edition_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Check if the current user has unlocked this edition."""
    is_unlocked = await is_edition_unlocked_for_user(db, current_user.id, edition_id)
    
    return {
        "edition_id": edition_id,
        "is_unlocked": is_unlocked
    }


@router.get("/unlocked-books")
async def get_unlocked_books(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get all books/editions the current user has unlocked."""
    # Get unlocked edition IDs with details
    unlocked_result = await db.execute(
        select(UnlockedBook, Edition)
        .join(Edition, UnlockedBook.edition_id == Edition.id)
        .where(UnlockedBook.user_id == current_user.id)
        .order_by(UnlockedBook.unlocked_at.desc())
    )
    
    unlocked_books = []
    for unlock, edition in unlocked_result.all():
        # Get book info
        from app.models import Book
        book_result = await db.execute(
            select(Book).where(Book.id == edition.book_id)
        )
        book = book_result.scalar_one_or_none()
        
        unlocked_books.append({
            "edition_id": edition.id,
            "book_title": book.title if book else "Unknown",
            "publisher": edition.publisher,
            "year": edition.year,
            "unlocked_at": unlock.unlocked_at,
            "review_id": unlock.review_id
        })
    
    return unlocked_books
