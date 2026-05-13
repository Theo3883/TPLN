from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class PreviewBookReview(Base):
    __tablename__ = "preview_book_reviews"

    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String(100), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    content = Column(Text, nullable=False)
    rating = Column(Float, nullable=True)
    status = Column(String(20), default="approved", nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Sentiment analysis fields
    sentiment_label = Column(String(20), nullable=True)
    sentiment_score = Column(Float, nullable=True)
    sentiment_confidence = Column(Float, nullable=True)

    # Gamification
    like_count = Column(Integer, default=0, nullable=False, index=True)

    # Relationships
    user = relationship("User")
