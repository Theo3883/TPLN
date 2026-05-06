from __future__ import annotations

from dataclasses import dataclass

import httpx


class ApiError(Exception):
    pass


@dataclass
class PlatformApiClient:
    base_url: str
    timeout: float = 30.0

    def _get(self, path: str, params: dict | None = None):
        try:
            with httpx.Client(base_url=self.base_url, timeout=self.timeout) as client:
                response = client.get(path, params=params)
        except Exception as exc:
            raise ApiError(str(exc)) from exc

        if response.status_code != 200:
            raise ApiError(f"{response.status_code}: {response.text}")
        return response.json()

    def _post(self, path: str, payload: dict | None = None):
        try:
            with httpx.Client(base_url=self.base_url, timeout=self.timeout) as client:
                response = client.post(path, json=payload)
        except Exception as exc:
            raise ApiError(str(exc)) from exc

        if response.status_code != 200:
            raise ApiError(f"{response.status_code}: {response.text}")
        return response.json() if response.text else {}

    def list_editions(self, limit: int = 90) -> list[dict]:
        return self._get("/editions", {"limit": limit})

    def get_edition(self, edition_id: int) -> dict:
        return self._get(f"/editions/{edition_id}")

    def search_editions(
        self,
        query: str,
        *,
        year_min: int | None = None,
        year_max: int | None = None,
        score_min: float | None = None,
        confidence_min: float | None = None,
        sort: str = "relevance",
    ) -> list[dict]:
        params = {
            "q": query,
            "sort": sort,
        }

        if year_min is not None:
            params["year_min"] = year_min
        if year_max is not None:
            params["year_max"] = year_max
        if score_min is not None:
            params["score_min"] = score_min
        if confidence_min is not None:
            params["confidence_min"] = confidence_min

        return self._get("/search/editions", params)

    def list_rankings(self, limit: int = 60) -> list[dict]:
        return self._get("/rankings", {"limit": limit})

    def get_edition_reviews(self, edition_id: int) -> list[dict]:
        return self._get(f"/editions/{edition_id}/reviews")

    def get_pending_reviews(self) -> list[dict]:
        return self._get("/moderation/pending")

    def approve_review(self, review_id: int) -> dict:
        return self._post(f"/moderation/{review_id}/approve")

    def reject_review(self, review_id: int) -> dict:
        return self._post(f"/moderation/{review_id}/reject")

    def create_review(
        self,
        *,
        edition_id: int,
        content: str,
        rating: float,
        reviewer_identifier: str,
    ) -> dict:
        payload = {
            "edition_id": edition_id,
            "content": content,
            "rating": rating,
            "reviewer_identifier": reviewer_identifier,
        }
        return self._post("/reviews", payload)

    def get_audit(self, edition_id: int) -> list[dict]:
        return self._get(f"/audit/editions/{edition_id}")

    def run_crawler(self) -> dict:
        return self._post("/ingest/run-crawler")
