"""Run Scrapy crawler from backend (subprocess)."""

import asyncio
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
CRAWLER_DIR = PROJECT_ROOT / "crawler"


async def _execute_crawler(delay_seconds: float = 0) -> None:
    if delay_seconds:
        await asyncio.sleep(delay_seconds)
    if not CRAWLER_DIR.exists():
        return
    env = os.environ.copy()
    env["PYTHONPATH"] = str(PROJECT_ROOT)
    proc = await asyncio.create_subprocess_exec(
        sys.executable,
        "-m",
        "scrapy",
        "crawl",
        "sample_ro_books",
        cwd=str(CRAWLER_DIR),
        env=env,
        stdout=asyncio.subprocess.DEVNULL,
        stderr=asyncio.subprocess.DEVNULL,
    )
    await proc.wait()


async def run_crawler() -> None:
    """Run sample_ro_books spider in background (with startup delay)."""
    await _execute_crawler(delay_seconds=3)


async def run_crawler_now() -> None:
    """Run crawler immediately (for manual trigger)."""
    await _execute_crawler(delay_seconds=0)
