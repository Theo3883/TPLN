"""
Endpoint-uri NLP sentiment — responsabilitatea Martinaș Ioana Maria.
Expune analiza de sentiment pentru recenzii românești bazată pe LaRoSeDa.
"""

import sys
import os

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models import Review, Edition

# Importă modulul NLP (cale relativă față de rădăcina proiectului)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../nlp/sentiment"))
from analyzer import analyze, SentimentResult  # noqa: E402

router = APIRouter()


# ---------------------------------------------------------------------------
# Scheme Pydantic pentru NLP
# ---------------------------------------------------------------------------

class SentimentRequest(BaseModel):
    """Input pentru analiza de sentiment pe text liber."""
    text: str = Field(
        ...,
        min_length=10,
        max_length=5000,
        description="Textul recenziei în limba română.",
    )

    @field_validator("text")
    @classmethod
    def text_must_not_be_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Textul nu poate fi gol sau format doar din spații.")
        return v.strip()


class SentimentResponse(BaseModel):
    """Rezultatul analizei de sentiment."""
    label: str = Field(..., description="'pozitiv', 'negativ' sau 'neutru'")
    score: float = Field(..., description="Scor sentiment în intervalul [-1.0, 1.0]")
    confidence: float = Field(..., description="Nivelul de încredere al predicției [0.0, 1.0]")
    positive_terms: list[str] = Field(default_factory=list, description="Termeni pozitivi detectați")
    negative_terms: list[str] = Field(default_factory=list, description="Termeni negativi detectați")
    detail: str = Field(..., description="Explicație human-readable a predicției")


class ReviewSentimentResponse(BaseModel):
    """Sentiment pentru o recenzie existentă din DB."""
    review_id: int
    edition_id: int
    content_preview: str = Field(..., description="Primele 100 de caractere ale recenziei")
    sentiment: SentimentResponse


class EditionSentimentSummary(BaseModel):
    """Rezumat sentiment pentru toate recenziile unei ediții."""
    edition_id: int
    total_reviews: int
    analyzed_reviews: int
    positive_count: int
    negative_count: int
    neutral_count: int
    average_score: float = Field(..., description="Scor mediu sentiment [-1.0, 1.0]")
    average_confidence: float
    overall_label: str = Field(..., description="Eticheta dominantă: 'pozitiv', 'negativ', 'neutru'")
    reviews: list[ReviewSentimentResponse]


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _to_response(result: SentimentResult) -> SentimentResponse:
    return SentimentResponse(
        label=result.label,
        score=result.score,
        confidence=result.confidence,
        positive_terms=result.positive_terms,
        negative_terms=result.negative_terms,
        detail=result.detail,
    )


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post(
    "/analyze",
    response_model=SentimentResponse,
    summary="Analizează sentimentul unui text românesc",
    description=(
        "Primește un text în română și returnează eticheta de sentiment "
        "(pozitiv/negativ/neutru), un scor în [-1, 1] și nivelul de încredere. "
        "Bazat pe lexiconul LaRoSeDa (Tache et al., EACL 2021)."
    ),
)
async def analyze_text(body: SentimentRequest) -> SentimentResponse:
    """
    Analizează sentimentul unui text liber în română.
    Nu necesită autentificare — util pentru testare din UI.
    """
    result = analyze(body.text)
    return _to_response(result)


@router.get(
    "/reviews/{review_id}",
    response_model=ReviewSentimentResponse,
    summary="Sentiment pentru o recenzie existentă",
    description="Returnează analiza de sentiment pentru recenzia cu ID-ul dat.",
)
async def get_review_sentiment(
    review_id: int,
    db: AsyncSession = Depends(get_db),
) -> ReviewSentimentResponse:
    """Analizează sentimentul unei recenzii existente din baza de date."""
    result = await db.execute(select(Review).where(Review.id == review_id))
    review = result.scalar_one_or_none()

    if not review:
        raise HTTPException(status_code=404, detail=f"Recenzia cu id={review_id} nu există.")

    sentiment = analyze(review.content)

    return ReviewSentimentResponse(
        review_id=review.id,
        edition_id=review.edition_id,
        content_preview=review.content[:100] + ("..." if len(review.content) > 100 else ""),
        sentiment=_to_response(sentiment),
    )


@router.get(
    "/editions/{edition_id}",
    response_model=EditionSentimentSummary,
    summary="Rezumat sentiment pentru toate recenziile unei ediții",
    description=(
        "Analizează toate recenziile aprobate ale unei ediții și returnează "
        "un rezumat agregat: distribuție pozitiv/negativ/neutru, scor mediu și eticheta dominantă."
    ),
)
async def get_edition_sentiment(
    edition_id: int,
    limit: int = Query(50, ge=1, le=200, description="Numărul maxim de recenzii de analizat"),
    db: AsyncSession = Depends(get_db),
) -> EditionSentimentSummary:
    """Agregează sentimentul tuturor recenziilor aprobate pentru o ediție."""
    # Verifică că ediția există
    ed_result = await db.execute(select(Edition).where(Edition.id == edition_id))
    if not ed_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail=f"Ediția cu id={edition_id} nu există.")

    # Ia recenziile aprobate
    rev_result = await db.execute(
        select(Review)
        .where(Review.edition_id == edition_id, Review.status == "approved")
        .limit(limit)
    )
    reviews = rev_result.scalars().all()

    if not reviews:
        return EditionSentimentSummary(
            edition_id=edition_id,
            total_reviews=0,
            analyzed_reviews=0,
            positive_count=0,
            negative_count=0,
            neutral_count=0,
            average_score=0.0,
            average_confidence=0.0,
            overall_label="neutru",
            reviews=[],
        )

    # Analizează fiecare recenzie
    review_results: list[ReviewSentimentResponse] = []
    scores: list[float] = []
    confidences: list[float] = []
    pos_count = neg_count = neu_count = 0

    for review in reviews:
        sentiment = analyze(review.content)
        scores.append(sentiment.score)
        confidences.append(sentiment.confidence)

        if sentiment.label == "pozitiv":
            pos_count += 1
        elif sentiment.label == "negativ":
            neg_count += 1
        else:
            neu_count += 1

        review_results.append(ReviewSentimentResponse(
            review_id=review.id,
            edition_id=review.edition_id,
            content_preview=review.content[:100] + ("..." if len(review.content) > 100 else ""),
            sentiment=_to_response(sentiment),
        ))

    avg_score = round(sum(scores) / len(scores), 4) if scores else 0.0
    avg_conf = round(sum(confidences) / len(confidences), 4) if confidences else 0.0

    # Eticheta dominantă
    counts = {"pozitiv": pos_count, "negativ": neg_count, "neutru": neu_count}
    overall = max(counts, key=lambda k: counts[k])

    return EditionSentimentSummary(
        edition_id=edition_id,
        total_reviews=len(reviews),
        analyzed_reviews=len(reviews),
        positive_count=pos_count,
        negative_count=neg_count,
        neutral_count=neu_count,
        average_score=avg_score,
        average_confidence=avg_conf,
        overall_label=overall,
        reviews=review_results,
    )