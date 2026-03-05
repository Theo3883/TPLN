"""Meilisearch client for edition search."""

from meilisearch import Client

from app.core.config import settings


def get_search_client() -> Client:
    return Client(settings.meilisearch_url, settings.meilisearch_api_key)


async def sync_edition_to_search(edition: dict) -> None:
    client = get_search_client()
    index = client.index(settings.meilisearch_index)
    index.add_documents([edition])
