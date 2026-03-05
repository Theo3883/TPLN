"""Anti-abuse: anomaly detection heuristics (KISS: thresholds, not ML)."""

from datetime import datetime, timedelta
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Review, Reviewer


async def check_review_anomaly(db: AsyncSession, reviewer_identifier: str) -> bool:
    """
    Returns True if anomaly detected (e.g. too many reviews from same identifier).
    """
    since = datetime.utcnow() - timedelta(hours=1)
    result = await db.execute(
        select(func.count(Review.id))
        .join(Reviewer, Review.reviewer_id == Reviewer.id)
        .where(Reviewer.identifier == reviewer_identifier, Review.created_at >= since)
    )
    count = result.scalar() or 0
    return count >= 10
