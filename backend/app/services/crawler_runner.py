"""Run crawlers from backend: executes run_all.py then ingests the JSON output."""

import asyncio
import json
import subprocess
import sys
from pathlib import Path

import httpx

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
CRAWLER_DIR = PROJECT_ROOT / "crawler"
CRAWLER_OUTPUT = CRAWLER_DIR / "output"
INGEST_URL = "http://localhost:8000/ingest"


def _run_crawlers_sync() -> None:
    """Execute run_all.py as a blocking subprocess (called from a thread)."""
    if not CRAWLER_DIR.exists():
        return
    subprocess.run(
        [sys.executable, "run_all.py"],
        cwd=str(CRAWLER_DIR),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


async def _run_crawlers() -> None:
    """Run the crawlers in a thread to avoid asyncio subprocess issues on Windows."""
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, _run_crawlers_sync)


async def _ingest_output() -> None:
    """Read crawler JSON output files and POST each book to /ingest."""
    if not CRAWLER_OUTPUT.exists():
        return
    async with httpx.AsyncClient(timeout=60.0) as client:
        for json_file in sorted(CRAWLER_OUTPUT.glob("*.json")):
            try:
                books = json.loads(json_file.read_text(encoding="utf-8"))
            except Exception:
                continue
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
                }
                try:
                    await client.post(INGEST_URL, json=payload)
                except Exception:
                    pass


async def _execute_crawler(delay_seconds: float = 0) -> None:
    if delay_seconds:
        await asyncio.sleep(delay_seconds)
    await _run_crawlers()
    await _ingest_output()


async def run_crawler() -> None:
    """Run crawlers in background (with startup delay)."""
    await _execute_crawler(delay_seconds=3)


async def run_crawler_now() -> None:
    """Run crawlers immediately (for manual trigger)."""
    await _execute_crawler(delay_seconds=0)
