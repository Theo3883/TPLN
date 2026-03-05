from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    edition_id = Column(Integer, ForeignKey("editions.id"), nullable=False, index=True)
    reviewer_id = Column(Integer, ForeignKey("reviewers.id"), nullable=False, index=True)
    content = Column(Text, nullable=False)
    rating = Column(Float, nullable=True)
    status = Column(String(20), default="pending", nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    edition = relationship("Edition", back_populates="reviews")
    reviewer = relationship("Reviewer", back_populates="reviews")
