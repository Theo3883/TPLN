from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.core.database import Base


class Reviewer(Base):
    __tablename__ = "reviewers"

    id = Column(Integer, primary_key=True, index=True)
    identifier = Column(String(255), nullable=False, unique=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    migrated = Column(Boolean, default=False, nullable=False)

    reviews = relationship("Review", back_populates="reviewer")
    user = relationship("User", back_populates="reviewer")
