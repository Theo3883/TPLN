"""
Scheme Pydantic pentru recenzii — cu validatori completi.
Responsabilitatea: Martinaș Ioana Maria (Backend API lead).
"""

from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, field_validator, model_validator


class SentimentLabel(str, Enum):
    """Etichete pentru clasificarea sentiment-ului."""
    POZITIV = "pozitiv"
    NEGATIV = "negativ"
    NEUTRU = "neutru"


class ReviewCreate(BaseModel):
    """
    Schema de creare recenzie cu validare completă.
    Câmpurile sunt validate strict înainte de a ajunge la endpoint.
    """
    edition_id: int = Field(..., gt=0, description="ID-ul ediției recenzate (trebuie să fie pozitiv)")
    content: str = Field(
        ...,
        min_length=20,
        max_length=5000,
        description="Textul recenziei (minim 20 caractere, maxim 5000)",
    )
    rating: float | None = Field(
        default=None,
        ge=1.0,
        le=5.0,
        description="Rating opțional între 1.0 și 5.0",
    )
    reviewer_identifier: str = Field(
        default="anonymous",
        max_length=255,
        description="Identificatorul recenzentului (ex: email sau username)",
    )

    @field_validator("content")
    @classmethod
    def content_must_not_be_blank(cls, v: str) -> str:
        """Conținutul nu poate fi doar spații goale."""
        stripped = v.strip()
        if not stripped:
            raise ValueError("Conținutul recenziei nu poate fi gol.")
        if len(stripped) < 20:
            raise ValueError("Recenzia trebuie să aibă cel puțin 20 de caractere semnificative.")
        return stripped

    @field_validator("reviewer_identifier")
    @classmethod
    def identifier_must_not_be_blank(cls, v: str) -> str:
        """Identificatorul nu poate fi gol."""
        if not v.strip():
            raise ValueError("reviewer_identifier nu poate fi gol.")
        return v.strip()

    @field_validator("rating")
    @classmethod
    def rating_step_validation(cls, v: float | None) -> float | None:
        """Ratingul trebuie să fie în pași de 0.5 (ex: 1.0, 1.5, 2.0 ... 5.0)."""
        if v is None:
            return v
        rounded = round(v * 2) / 2
        if abs(rounded - v) > 0.01:
            raise ValueError("Ratingul trebuie să fie un multiplu de 0.5 (ex: 1.0, 1.5, 2.0...5.0)")
        return rounded


class ReviewResponse(BaseModel):
    """Schema de răspuns pentru o recenzie."""
    id: int
    edition_id: int
    content: str
    rating: float | None = None
    status: str
    created_at: datetime
    # Câmpuri sentiment — populat automat după creare
    sentiment_label: SentimentLabel | None = Field(
        default=None,
        description="Eticheta de sentiment: pozitiv, negativ sau neutru",
    )
    sentiment_score: float | None = Field(
        default=None,
        description="Scor sentiment în [-1.0, 1.0] sau None dacă nu e calculat",
    )
    sentiment_confidence: float | None = Field(
        default=None,
        description="Confidence score al modelului NLP în [0.0, 1.0]",
    )
    # Gamification fields
    like_count: int = Field(default=0, description="Numărul de like-uri primite")
    liked_by_user: bool = Field(default=False, description="Dacă utilizatorul curent a apreciat review-ul")

    class Config:
        from_attributes = True