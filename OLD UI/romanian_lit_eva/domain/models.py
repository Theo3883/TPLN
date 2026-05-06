from dataclasses import dataclass


@dataclass(frozen=True)
class EditionCard:
    id: int
    title: str
    authors: str
    publisher: str
    year: str
    isbn: str
    score: float
    confidence: float
    review_count: int


@dataclass(frozen=True)
class ReviewItem:
    id: int
    edition_id: int
    content: str
    rating: float | None
    status: str
    created_at: str


@dataclass(frozen=True)
class RankingItem:
    edition_id: int
    title: str
    authors: str
    score: float
    confidence: float
    review_count: int


@dataclass(frozen=True)
class AuditItem:
    id: int
    reason: str
    old_score: float | None
    new_score: float | None
    created_at: str
