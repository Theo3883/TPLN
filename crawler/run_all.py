"""Run all three book crawlers and print a summary."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

SCRIPTS = [
    "crawl_bookzone.py",
    "crawl_libris.py",
    "crawl_carturesti.py",
]


def main():
    base = Path(__file__).parent
    for script in SCRIPTS:
        path = base / script
        print(f"\n{'=' * 60}")
        print(f"  {script}")
        print(f"{'=' * 60}\n")
        result = subprocess.run([sys.executable, str(path)], cwd=str(base))
        if result.returncode != 0:
            print(f"\nWARNING: {script} exited with code {result.returncode}")

    # Summary
    output_dir = base / "output"
    print(f"\n{'=' * 60}")
    print("  Summary")
    print(f"{'=' * 60}")
    for f in sorted(output_dir.glob("*.json")):
        data = json.loads(f.read_text(encoding="utf-8"))
        with_isbn = sum(1 for b in data if b.get("isbn"))
        print(f"  {f.name}: {len(data)} books ({with_isbn} with ISBN)")


if __name__ == "__main__":
    main()
