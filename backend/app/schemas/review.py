from datetime import datetime
from pydantic import BaseModel


class ReviewCreate(BaseModel):
    edition_id: int
    content: str
    rating: float | None = None
    reviewer_identifier: str = "anonymous"


class ReviewResponse(BaseModel):
    id: int
    edition_id: int
    content: str
    rating: float | None = None
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
