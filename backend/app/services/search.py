"""Meilisearch client and helpers for edition search."""

from meilisearch import Client

from app.core.config import settings


def get_search_client() -> Client:
    return Client(settings.meilisearch_url, settings.meilisearch_api_key)


def configure_search_index() -> None:
    client = get_search_client()

    try:
        client.create_index(settings.meilisearch_index, {"primaryKey": "id"})
    except Exception:
        pass

    index = client.index(settings.meilisearch_index)

    index.update_searchable_attributes([
        "title",
        "authors",
        "isbn",
        "publisher",
    ])

    index.update_filterable_attributes([
        "year",
        "publisher",
        "score",
        "confidence",
        "review_count",
    ])

    index.update_sortable_attributes([
        "year",
        "score",
        "confidence",
        "review_count",
    ])


def build_search_document(edition, book, authors) -> dict:
    return {
        "id": edition.id,
        "title": book.title if book else "",
        "authors": " ".join(a.name for a in authors),
        "isbn": edition.isbn or "",
        "publisher": edition.publisher or "",
        "year": edition.year or 0,
        "score": float(edition.score or 0),
        "confidence": float(edition.confidence or 0),
        "review_count": int(edition.review_count or 0),
    }


async def sync_edition_to_search(edition, book, authors) -> None:
    client = get_search_client()
    index = client.index(settings.meilisearch_index)
    doc = build_search_document(edition, book, authors)
    index.add_documents([doc])