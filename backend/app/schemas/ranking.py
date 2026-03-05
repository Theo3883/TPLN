from pydantic import BaseModel


class RankingItem(BaseModel):
    edition_id: int
    title: str
    authors: list[str]
    score: float
    confidence: float
    review_count: int
