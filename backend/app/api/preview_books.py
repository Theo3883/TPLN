"""
preview_books.py — API for serving book previews (first 10 pages) and full books (unlocked).
Books are stored as PDFs in the /books folder at the project root.
"""

import io
import os
from pathlib import Path

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from pypdf import PdfReader, PdfWriter

from app.core.database import get_db
from app.core.security import get_current_user

router = APIRouter()

BOOKS_DIR = Path(__file__).resolve().parents[3] / "books"

# Book catalog — maps slug to metadata
PREVIEW_BOOKS = [
    {
        "slug": "crima-si-pedeapsa",
        "title": "Crimă și Pedeapsă",
        "author": "Feodor Mihailovici Dostoievski",
        "pdf": "crima-si-pedeapsa-feodor-mihailovici-dostoievski.pdf",
        "cover": "crima_si_pedeapsa.png",
        "pages": 10,
    },
    {
        "slug": "enigma-otiliei",
        "title": "Enigma Otiliei",
        "author": "George Călinescu",
        "pdf": "enigma-otiliei-george-calinescu.pdf",
        "cover": "enigma.png",
        "pages": 10,
    },
    {
        "slug": "psihologia-minciunii",
        "title": "Psihologia Minciunii",
        "author": "M. Scott Peck",
        "pdf": "psihologia-minciunii-m-scott-peck.pdf",
        "cover": "psihologia_minciunii.png",
        "pages": 10,
    },
    {
        "slug": "ultima-noapte",
        "title": "Ultima Noapte de Dragoste, Întâia Noapte de Război",
        "author": "Camil Petrescu",
        "pdf": "ultima-noapte-de-dragoste-intaia-noapte-de-razboi-camil-petrescu.pdf",
        "cover": "ultima_noapte.png",
        "pages": 10,
    },
]


@router.get("/preview-books")
async def list_preview_books():
    """List all available preview books with metadata."""
    result = []
    for book in PREVIEW_BOOKS:
        result.append({
            "slug": book["slug"],
            "title": book["title"],
            "author": book["author"],
            "pages": book["pages"],
            "cover_url": f"/preview-books/{book['slug']}/cover",
        })
    return result


@router.get("/preview-books/{slug}/cover")
async def get_book_cover(slug: str):
    """Serve the cover image for a preview book."""
    book = next((b for b in PREVIEW_BOOKS if b["slug"] == slug), None)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    cover_path = BOOKS_DIR / book["cover"]
    if not cover_path.is_file():
        raise HTTPException(status_code=404, detail="Cover image not found")
    
    return FileResponse(cover_path, media_type="image/png")


MAX_PREVIEW_PAGES = 10


@router.get("/preview-books/{slug}/preview")
async def get_book_preview(slug: str):
    """Serve only the first 10 pages of a PDF as a preview."""
    book = next((b for b in PREVIEW_BOOKS if b["slug"] == slug), None)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    pdf_path = BOOKS_DIR / book["pdf"]
    if not pdf_path.is_file():
        raise HTTPException(status_code=404, detail="PDF not found")
    
    reader = PdfReader(str(pdf_path))
    writer = PdfWriter()
    
    pages_to_copy = min(len(reader.pages), MAX_PREVIEW_PAGES)
    for i in range(pages_to_copy):
        writer.add_page(reader.pages[i])
    
    buf = io.BytesIO()
    writer.write(buf)
    buf.seek(0)
    
    return StreamingResponse(
        buf,
        media_type="application/pdf",
        headers={"Content-Disposition": f"inline; filename=\"preview-{slug}.pdf\""},
    )


@router.get("/preview-books/{slug}/full")
async def get_full_book(
    slug: str,
    user=Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """Serve the full PDF — only if the user has unlocked it (most liked review)."""
    from app.services.unlock_service import get_user_unlocked_editions

    book = next((b for b in PREVIEW_BOOKS if b["slug"] == slug), None)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    # Check if user has any unlocked editions (gift books)
    unlocked = await get_user_unlocked_editions(session, user.id)
    # For preview books, we check by slug match in a simple mapping
    # Since these are standalone PDFs, we grant access if user has ANY unlock
    if not unlocked:
        raise HTTPException(
            status_code=403,
            detail="You haven't unlocked this book yet. Get the most liked review to unlock!",
        )

    pdf_path = BOOKS_DIR / book["pdf"]
    if not pdf_path.is_file():
        raise HTTPException(status_code=404, detail="PDF not found")

    return FileResponse(
        pdf_path,
        media_type="application/pdf",
        headers={"Content-Disposition": f"inline; filename=\"{slug}.pdf\""},
    )


# --- Reviews for preview books ---

from pydantic import BaseModel, Field
from typing import Optional
from sqlalchemy import select
from app.models.preview_book_review import PreviewBookReview
from app.core.security import get_current_user_optional


class PreviewReviewCreate(BaseModel):
    content: str = Field(..., min_length=20, max_length=5000)
    rating: Optional[float] = Field(None, ge=1.0, le=5.0)


class PreviewReviewResponse(BaseModel):
    id: int
    slug: str
    user_id: int
    username: str
    content: str
    rating: Optional[float]
    status: str
    created_at: str
    sentiment_label: Optional[str]
    sentiment_score: Optional[float]
    sentiment_confidence: Optional[float]
    like_count: int
    liked_by_user: bool = False

    class Config:
        from_attributes = True


def _validate_slug(slug: str):
    book = next((b for b in PREVIEW_BOOKS if b["slug"] == slug), None)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


@router.get("/preview-books/{slug}/reviews")
async def list_preview_reviews(
    slug: str,
    current_user=Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db),
):
    """List all reviews for a preview book."""
    _validate_slug(slug)

    result = await db.execute(
        select(PreviewBookReview)
        .where(PreviewBookReview.slug == slug)
        .order_by(PreviewBookReview.like_count.desc(), PreviewBookReview.created_at.desc())
    )
    reviews = result.scalars().all()

    response = []
    for r in reviews:
        # Get username
        from app.models.user import User as UserModel
        user_result = await db.execute(select(UserModel).where(UserModel.id == r.user_id))
        user_obj = user_result.scalar_one_or_none()

        response.append(PreviewReviewResponse(
            id=r.id,
            slug=r.slug,
            user_id=r.user_id,
            username=user_obj.username if user_obj else "Unknown",
            content=r.content,
            rating=r.rating,
            status=r.status,
            created_at=r.created_at.isoformat() if r.created_at else "",
            sentiment_label=r.sentiment_label,
            sentiment_score=r.sentiment_score,
            sentiment_confidence=r.sentiment_confidence,
            like_count=r.like_count,
            liked_by_user=False,
        ))

    return response


@router.post("/preview-books/{slug}/reviews")
async def create_preview_review(
    slug: str,
    review_in: PreviewReviewCreate,
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a review for a preview book (requires authentication)."""
    _validate_slug(slug)

    # Sentiment analysis
    from app.services.sentiment_analyzer import analyze_review_sentiment
    sentiment = await analyze_review_sentiment(review_in.content)

    review = PreviewBookReview(
        slug=slug,
        user_id=user.id,
        content=review_in.content,
        rating=review_in.rating,
        sentiment_label=sentiment["label"],
        sentiment_score=sentiment["score"],
        sentiment_confidence=sentiment["confidence"],
    )
    db.add(review)
    await db.commit()
    await db.refresh(review)

    return PreviewReviewResponse(
        id=review.id,
        slug=review.slug,
        user_id=review.user_id,
        username=user.username,
        content=review.content,
        rating=review.rating,
        status=review.status,
        created_at=review.created_at.isoformat() if review.created_at else "",
        sentiment_label=review.sentiment_label,
        sentiment_score=review.sentiment_score,
        sentiment_confidence=review.sentiment_confidence,
        like_count=review.like_count,
        liked_by_user=False,
    )
