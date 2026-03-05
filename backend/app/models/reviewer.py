from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.core.database import Base


class Reviewer(Base):
    __tablename__ = "reviewers"

    id = Column(Integer, primary_key=True, index=True)
    identifier = Column(String(255), nullable=False, unique=True, index=True)

    reviews = relationship("Review", back_populates="reviewer")
