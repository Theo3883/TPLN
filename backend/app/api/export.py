import csv
import io
from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models import Edition

router = APIRouter()


@router.get("")
async def export_data(
    format: str = Query("csv", regex="^(csv|json)$"),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Edition).options(selectinload(Edition.book), selectinload(Edition.authors))
    )
    editions = result.scalars().all()

    if format == "csv":
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["id", "title", "authors", "isbn", "publisher", "year", "score", "confidence", "review_count"])
        for e in editions:
            authors_str = "; ".join(a.name for a in e.authors)
            writer.writerow([
                e.id,
                e.book.title if e.book else "",
                authors_str,
                e.isbn or "",
                e.publisher or "",
                e.year or "",
                e.score or "",
                e.confidence or "",
                e.review_count,
            ])
        output.seek(0)
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=editions.csv"},
        )

    import json
    data = [
        {
            "id": e.id,
            "title": e.book.title if e.book else "",
            "authors": [a.name for a in e.authors],
            "isbn": e.isbn,
            "publisher": e.publisher,
            "year": e.year,
            "score": e.score,
            "confidence": e.confidence,
            "review_count": e.review_count,
        }
        for e in editions
    ]
    return StreamingResponse(
        iter([json.dumps(data, ensure_ascii=False, indent=2)]),
        media_type="application/json",
        headers={"Content-Disposition": "attachment; filename=editions.json"},
    )
