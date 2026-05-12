"""
Service for managing book unlocks via top-liked reviews.
Handles automatic unlock/lock when review like counts change.
"""
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Review, UnlockedBook, User, Edition


async def get_top_review_for_edition(db: AsyncSession, edition_id: int) -> Review | None:
    """
    Get the review with the highest like_count for an edition.
    Returns None if no reviews exist or all have 0 likes.
    """
    result = await db.execute(
        select(Review)
        .where(
            and_(
                Review.edition_id == edition_id,
                Review.status.in_(["approved", "pending"]),  # Only count approved/pending reviews
                Review.like_count > 0  # Must have at least 1 like to unlock
            )
        )
        .order_by(Review.like_count.desc(), Review.created_at.asc())  # Tie-breaker: older review wins
        .limit(1)
    )
    return result.scalar_one_or_none()


async def check_and_update_unlocks(db: AsyncSession, edition_id: int) -> dict:
    """
    Recalculate which user (if any) has unlocked this edition.
    Called after any like count change.
    
    Returns:
        dict with keys: 'unlocked_user_id', 'locked_user_ids', 'top_review_id'
    """
    top_review = await get_top_review_for_edition(db, edition_id)
    
    # Get current unlock for this edition
    current_unlock_result = await db.execute(
        select(UnlockedBook).where(UnlockedBook.edition_id == edition_id)
    )
    current_unlock = current_unlock_result.scalar_one_or_none()
    
    unlocked_user_id = None
    locked_user_ids = []
    
    if top_review:
        # Get the reviewer's user_id
        reviewer_result = await db.execute(
            select(Review.reviewer_id).where(Review.id == top_review.id)
        )
        reviewer = await db.execute(
            select(User.id)
            .join(User.reviewer)
            .where(User.reviewer.has(id=top_review.reviewer_id))
        )
        top_user = reviewer.scalar_one_or_none()
        
        if top_user:
            # Check if the current top is different from existing unlock
            if current_unlock and current_unlock.user_id != top_user:
                # Lock old user
                locked_user_ids.append(current_unlock.user_id)
                await db.delete(current_unlock)
                await db.flush()
                current_unlock = None
            
            # Create new unlock if needed
            if not current_unlock or current_unlock.user_id != top_user:
                new_unlock = UnlockedBook(
                    user_id=top_user,
                    edition_id=edition_id,
                    review_id=top_review.id
                )
                db.add(new_unlock)
                await db.flush()
                unlocked_user_id = top_user
    else:
        # No top review (all reviews have 0 likes or no reviews)
        if current_unlock:
            locked_user_ids.append(current_unlock.user_id)
            await db.delete(current_unlock)
            await db.flush()
    
    return {
        "unlocked_user_id": unlocked_user_id,
        "locked_user_ids": locked_user_ids,
        "top_review_id": top_review.id if top_review else None
    }


async def is_edition_unlocked_for_user(db: AsyncSession, user_id: int, edition_id: int) -> bool:
    """Check if a specific user has unlocked access to an edition."""
    result = await db.execute(
        select(UnlockedBook).where(
            and_(
                UnlockedBook.user_id == user_id,
                UnlockedBook.edition_id == edition_id
            )
        )
    )
    return result.scalar_one_or_none() is not None


async def get_user_unlocked_editions(db: AsyncSession, user_id: int) -> list[int]:
    """Get all edition IDs that a user has unlocked."""
    result = await db.execute(
        select(UnlockedBook.edition_id).where(UnlockedBook.user_id == user_id)
    )
    return [row[0] for row in result.all()]
