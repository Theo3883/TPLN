from datetime import datetime
from enum import Enum
from pydantic import BaseModel


class EditionSource(str, Enum):
    """Source of edition data."""
    MANUAL = "manual"
    CRAWLER = "crawler"


class CrawlerName(str, Enum):
    """Names of supported crawlers."""
    BOOKZONE = "bookzone"
    CARTURESTI = "carturesti"
    LIBRIS = "libris"


class AuthorSchema(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class BookSchema(BaseModel):
    id: int
    title: str

    class Config:
        from_attributes = True


class EditionBase(BaseModel):
    isbn: str | None = None
    publisher: str | None = None
    year: int | None = None


class EditionCreate(EditionBase):
    book_id: int
    author_ids: list[int] = []


class EditionResponse(EditionBase):
    id: int
    book_id: int
    score: float | None = None
    confidence: float | None = None
    review_count: int = 0
    book: BookSchema | None = None
    authors: list[AuthorSchema] = []
    
    # Source tracking fields
    source: EditionSource = EditionSource.MANUAL
    crawler_name: CrawlerName | None = None
    imported_at: datetime | None = None
    
    # Preview text for review eligibility
    preview_text: str | None = None

    class Config:
        from_attributes = True
