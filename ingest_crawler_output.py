import json
from pathlib import Path

import httpx


API_URL = "http://localhost:8000/ingest"
OUTPUT_DIR = Path("crawler/output")

FILES = [
    "bookzone.json",
    "carturesti.json",
    "libris.json",
]


def get_crawler_name(filename: str) -> str:
    """Extract crawler name from filename (e.g., 'bookzone.json' -> 'bookzone')."""
    return Path(filename).stem


def normalize_item(item: dict, crawler_name: str) -> dict:
    """Normalize crawler output item and add crawler_name."""
    return {
        "title": item.get("title") or "",
        "authors": item.get("authors") or [],
        "isbn": item.get("isbn"),
        "publisher": item.get("publisher"),
        "year": item.get("year"),
        "crawler_name": crawler_name,  # Add crawler tracking
    }


def main():
    total = 0
    created = 0
    duplicates = 0
    errors = 0

    with httpx.Client(timeout=30.0) as client:
        for filename in FILES:
            path = OUTPUT_DIR / filename

            if not path.exists():
                print(f"[SKIP] {path} does not exist")
                continue

            crawler_name = get_crawler_name(filename)
            with path.open("r", encoding="utf-8") as f:
                items = json.load(f)

            print(f"\nImporting {filename} ({crawler_name}): {len(items)} items")

            for item in items:
                total += 1
                payload = normalize_item(item, crawler_name)

                if not payload["title"]:
                    errors += 1
                    continue

                try:
                    response = client.post(API_URL, json=payload)
                    response.raise_for_status()
                    data = response.json()

                    if data.get("status") == "created":
                        created += 1
                    elif data.get("status") == "duplicate":
                        duplicates += 1

                except Exception as exc:
                    errors += 1
                    print(f"[ERROR] {payload.get('title')}: {exc}")

    print("\nDone.")
    print(f"Total: {total}")
    print(f"Created: {created}")
    print(f"Duplicates: {duplicates}")
    print(f"Errors: {errors}")


if __name__ == "__main__":
    main()