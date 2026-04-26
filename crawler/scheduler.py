"""Hourly scheduler – runs all crawlers once immediately, then every hour."""
from __future__ import annotations

import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

INTERVAL_SECONDS = 3600  # 1 hour


def run_crawlers() -> None:
    script = Path(__file__).parent / "run_all.py"
    print(f"\n[{datetime.now():%Y-%m-%d %H:%M:%S}] Starting crawl run...")
    result = subprocess.run([sys.executable, str(script)], cwd=str(script.parent))
    if result.returncode == 0:
        print(f"[{datetime.now():%Y-%m-%d %H:%M:%S}] Crawl run completed successfully.")
    else:
        print(f"[{datetime.now():%Y-%m-%d %H:%M:%S}] Crawl run finished with errors (exit code {result.returncode}).")


def main() -> None:
    print(f"Crawler scheduler started. Interval: {INTERVAL_SECONDS // 60} minutes.")
    print("Press Ctrl+C to stop.\n")

    while True:
        run_crawlers()
        next_run = datetime.fromtimestamp(time.time() + INTERVAL_SECONDS)
        print(f"Next run at: {next_run:%Y-%m-%d %H:%M:%S}")
        try:
            time.sleep(INTERVAL_SECONDS)
        except KeyboardInterrupt:
            print("\nScheduler stopped.")
            sys.exit(0)


if __name__ == "__main__":
    main()
