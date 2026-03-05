from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class ScoreEvent(Base):
    __tablename__ = "score_events"

    id = Column(Integer, primary_key=True, index=True)
    edition_id = Column(Integer, ForeignKey("editions.id"), nullable=False, index=True)
    old_score = Column(Float, nullable=True)
    new_score = Column(Float, nullable=True)
    reason = Column(String(100), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    edition = relationship("Edition", back_populates="score_events")
