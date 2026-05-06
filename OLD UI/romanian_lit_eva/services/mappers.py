from __future__ import annotations

from romanian_lit_eva.domain.models import AuditItem, EditionCard, RankingItem, ReviewItem


def to_edition_card(raw: dict) -> EditionCard:
    authors = ", ".join(a.get("name", "") for a in raw.get("authors", [])) or "Unknown author"
    book = raw.get("book") or {}
    return EditionCard(
        id=raw["id"],
        title=book.get("title") or "N/A",
        authors=authors,
        publisher=raw.get("publisher") or "Unknown publisher",
        year=str(raw.get("year") or "-"),
        isbn=raw.get("isbn") or "-",
        score=float(raw.get("score") or 0),
        confidence=float(raw.get("confidence") or 0),
        review_count=int(raw.get("review_count") or 0),
    )


def to_ranking_item(raw: dict) -> RankingItem:
    return RankingItem(
        edition_id=raw["edition_id"],
        title=raw.get("title") or "N/A",
        authors=", ".join(raw.get("authors", [])) or "Unknown author",
        score=float(raw.get("score") or 0),
        confidence=float(raw.get("confidence") or 0),
        review_count=int(raw.get("review_count") or 0),
    )


def to_review_item(raw: dict) -> ReviewItem:
    return ReviewItem(
        id=raw["id"],
        edition_id=raw["edition_id"],
        content=raw.get("content") or "",
        rating=raw.get("rating"),
        status=raw.get("status") or "pending",
        created_at=raw.get("created_at") or "",
    )


def to_audit_item(raw: dict) -> AuditItem:
    return AuditItem(
        id=raw["id"],
        reason=raw.get("reason") or "update",
        old_score=raw.get("old_score"),
        new_score=raw.get("new_score"),
        created_at=raw.get("created_at") or "",
    )
