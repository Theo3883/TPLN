"""UnlockedBook model for tracking which books users have unlocked via top reviews."""
from sqlalchemy import Column, Integer, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from app.core.database import Base


class UnlockedBook(Base):
    """
    Tracks which books/editions users have unlocked.
    A user unlocks a book when their review becomes the top-liked review.
    Constraint: one user can unlock an edition only once (current top review).
    """
    __tablename__ = "unlocked_books"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    edition_id = Column(Integer, ForeignKey("editions.id", ondelete="CASCADE"), nullable=False, index=True)
    review_id = Column(Integer, ForeignKey("reviews.id", ondelete="CASCADE"), nullable=False, index=True)
    unlocked_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    user = relationship("User", back_populates="unlocked_books")
    edition = relationship("Edition", back_populates="unlocks")
    review = relationship("Review", back_populates="unlocks")

    # Constraints
    __table_args__ = (
        UniqueConstraint('user_id', 'edition_id', name='uq_user_edition_unlock'),
    )
