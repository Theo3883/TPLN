from datetime import datetime
from pydantic import BaseModel


class ScoreEventResponse(BaseModel):
    id: int
    edition_id: int
    old_score: float | None
    new_score: float | None
    reason: str
    created_at: datetime

    class Config:
        from_attributes = True
