"""
Ingest crawler JSON output files into the database via the backend API.

Usage (from repo root, with backend running):
    python ingest_crawler_output.py

Optional arguments:
    --api   Base URL of the backend (default: http://localhost:8000)
    --dir   Path to crawler output folder (default: crawler/output)
"""
import argparse
import json
from pathlib import Path

import httpx


def ingest(api_base: str, output_dir: Path) -> None:
    if not output_dir.exists():
        print(f"[ERROR] Output directory not found: {output_dir}")
        return

    json_files = sorted(output_dir.glob("*.json"))
    if not json_files:
        print(f"[ERROR] No JSON files found in {output_dir}")
        return

    total_created = 0
    total_duplicate = 0
    total_error = 0

    with httpx.Client(base_url=api_base, timeout=30) as client:
        for json_file in json_files:
            books = json.loads(json_file.read_text(encoding="utf-8"))
            created = duplicate = error = 0

            for book in books:
                title = (book.get("title") or "").strip()
                if not title:
                    continue
                payload = {
                    "title": title,
                    "authors": book.get("authors") or [],
                    "isbn": book.get("isbn") or None,
                    "publisher": book.get("publisher") or None,
                    "year": book.get("year") or None,
                    "cover_image": book.get("cover_image") or None,
                }
                try:
                    r = client.post("/ingest", json=payload)
                    r.raise_for_status()
                    status = r.json().get("status")
                    if status == "created":
                        created += 1
                    else:
                        duplicate += 1
                except Exception as exc:
                    error += 1
                    print(f"  [WARN] Failed to ingest '{title}': {exc}")

            print(
                f"  {json_file.name:<25} "
                f"{created:>3} created  "
                f"{duplicate:>3} duplicate  "
                f"{error:>3} error"
            )
            total_created += created
            total_duplicate += duplicate
            total_error += error

    print()
    print(f"Total: {total_created} created, {total_duplicate} duplicate, {total_error} error")


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest crawler output into the database.")
    parser.add_argument("--api", default="http://localhost:8000", help="Backend base URL")
    parser.add_argument("--dir", default="crawler/output", help="Crawler output directory")
    args = parser.parse_args()

    output_dir = Path(args.dir)
    print(f"Ingesting from : {output_dir.resolve()}")
    print(f"Backend API    : {args.api}")
    print()

    ingest(api_base=args.api, output_dir=output_dir)


if __name__ == "__main__":
    main()
