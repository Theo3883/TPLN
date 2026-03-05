from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base

edition_authors = Table(
    "edition_authors",
    Base.metadata,
    Column("edition_id", Integer, ForeignKey("editions.id"), primary_key=True),
    Column("author_id", Integer, ForeignKey("authors.id"), primary_key=True),
)


class Edition(Base):
    __tablename__ = "editions"

    id = Column(Integer, primary_key=True, index=True)
    book_id = Column(Integer, ForeignKey("books.id"), nullable=False, index=True)
    isbn = Column(String(17), unique=True, nullable=True, index=True)
    publisher = Column(String(255), nullable=True)
    year = Column(Integer, nullable=True)
    score = Column(Float, nullable=True)
    confidence = Column(Float, nullable=True)
    review_count = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    book = relationship("Book", back_populates="editions")
    authors = relationship(
        "Author",
        secondary=edition_authors,
        back_populates="editions",
    )
    reviews = relationship("Review", back_populates="edition")
    score_events = relationship("ScoreEvent", back_populates="edition")
