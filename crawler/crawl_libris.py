"""
Libris.ro crawler — BeautifulSoup + httpx.

Strategy:
  1. Fetch the /carti listing page and several category pages to
     collect /carte/ detail-page URLs from static HTML.
  2. Visit each detail page and extract metadata from JSON-LD (@graph).

Output: output/libris.json
"""
from __future__ import annotations

import json
import re
import time
from pathlib import Path

import httpx
from bs4 import BeautifulSoup

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
OUTPUT_DIR = Path(__file__).parent / "output"
OUTPUT_FILE = OUTPUT_DIR / "libris.json"

BASE_URL = "https://www.libris.ro"
SEED_URL = f"{BASE_URL}/carti"
DELAY = 3
MAX_CATEGORIES = 8   # how many sub-category pages to visit
MAX_BOOKS = 200

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (compatible; LitPlatformBot/1.0; educational project)"
    ),
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def normalize_isbn(raw):
    if not raw:
        return None
    digits = "".join(c for c in str(raw) if c.isdigit())
    return digits if len(digits) in (10, 13) else None


def parse_year(raw):
    if not raw:
        return None
    m = re.search(r"\b(19|20)\d{2}\b", str(raw))
    return int(m.group()) if m else None


def extract_graph_product(soup):
    """Find a Product/Book item inside a JSON-LD @graph array."""
    for script in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(script.string)
            # Direct item
            if isinstance(data, dict):
                t = data.get("@type", "")
                types = t if isinstance(t, list) else [t]
                if "Product" in types or "Book" in types:
                    return data
                # Check @graph
                for item in data.get("@graph", []):
                    t2 = item.get("@type", "")
                    types2 = t2 if isinstance(t2, list) else [t2]
                    if "Product" in types2 or "Book" in types2:
                        return item
            # Top-level list
            if isinstance(data, list):
                for item in data:
                    t = item.get("@type", "")
                    types = t if isinstance(t, list) else [t]
                    if "Product" in types or "Book" in types:
                        return item
        except (json.JSONDecodeError, TypeError):
            continue
    return None


# ---------------------------------------------------------------------------
# URL discovery
# ---------------------------------------------------------------------------
def _extract_book_links(soup):
    """Return unique /carte/ URLs found on the page."""
    seen = set()
    urls = []
    for a in soup.find_all("a", href=re.compile(r"/carte/")):
        href = a["href"].split("?")[0]
        full = href if href.startswith("http") else BASE_URL + href
        if full not in seen:
            seen.add(full)
            urls.append(full)
    return urls


def _extract_category_links(soup):
    """Return sub-category URLs like /carti/beletristica."""
    seen = set()
    urls = []
    for a in soup.find_all("a", href=re.compile(r"^/carti/[a-z]")):
        href = a["href"].split("?")[0]
        # Only one level deep (e.g. /carti/beletristica)
        parts = href.strip("/").split("/")
        if len(parts) == 2:
            full = BASE_URL + href
            if full not in seen:
                seen.add(full)
                urls.append(full)
    return urls


def collect_book_urls(client):
    """Gather book detail URLs from the main listing + category pages."""
    all_book_urls = []
    all_seen = set()

    def _add(urls):
        for u in urls:
            if u not in all_seen:
                all_seen.add(u)
                all_book_urls.append(u)

    # 1) Main listing
    print("  Main listing page...")
    r = client.get(SEED_URL)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    book_links = _extract_book_links(soup)
    _add(book_links)
    print(f"    {len(book_links)} book URLs")

    # Discover categories
    categories = _extract_category_links(soup)
    print(f"    {len(categories)} category links found")
    time.sleep(DELAY)

    # 2) Visit category pages for more book links
    for cat_url in categories[:MAX_CATEGORIES]:
        slug = cat_url.split("/carti/")[-1]
        print(f"  Category: {slug}...", end=" ")
        try:
            r2 = client.get(cat_url)
            r2.raise_for_status()
            soup2 = BeautifulSoup(r2.text, "html.parser")
            links = _extract_book_links(soup2)
            before = len(all_book_urls)
            _add(links)
            new = len(all_book_urls) - before
            print(f"{new} new URLs")
        except Exception as e:
            print(f"error: {e}")
        time.sleep(DELAY)

    return all_book_urls


# ---------------------------------------------------------------------------
# Detail page
# ---------------------------------------------------------------------------
def parse_book(client, url):
    r = client.get(url)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")

    ld = extract_graph_product(soup)
    if not ld:
        return None

    # Title — Libris puts "Title - Author" in the name field
    title = (ld.get("name") or "").strip()
    if " - " in title:
        title = title.rsplit(" - ", 1)[0].strip()
    if not title:
        return None

    # Authors
    raw = ld.get("author", [])
    if isinstance(raw, list):
        authors = [
            (a["name"].strip() if isinstance(a, dict) else str(a).strip())
            for a in raw
        ]
    elif isinstance(raw, dict):
        authors = [raw.get("name", "").strip()]
    elif isinstance(raw, str):
        authors = [s.strip() for s in raw.split(",")]
    else:
        authors = []
    # Fallback: /autor/ links
    if not authors:
        for tag in soup.find_all("a", href=re.compile(r"/autor/")):
            name = tag.get_text(strip=True)
            clean = re.sub(r"^Autor:\s*", "", name).strip()
            if clean and clean not in authors:
                authors.append(clean)

    # ISBN
    isbn = normalize_isbn(ld.get("isbn") or ld.get("gtin13"))

    # Publisher
    pub = ld.get("publisher", "")
    if isinstance(pub, dict):
        pub = pub.get("name", "")
    publisher = pub.strip() or None
    if not publisher:
        tag = soup.find("a", href=re.compile(r"/editura/"))
        if tag:
            publisher = re.sub(r"^Editura:\s*", "", tag.get_text(strip=True)).strip()

    # Year
    year = parse_year(ld.get("datePublished"))

    # Image
    img = ld.get("image") or ""
    if isinstance(img, dict):
        img = img.get("url", "")
    cover_image = img.strip() or None
    if not cover_image:
        og = soup.find("meta", property="og:image")
        if og:
            cover_image = og.get("content", "").strip() or None

    return {
        "title": title,
        "authors": authors,
        "isbn": isbn,
        "publisher": publisher,
        "year": year,
        "cover_image": cover_image,
        "source_url": url,
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    OUTPUT_DIR.mkdir(exist_ok=True)
    books = []
    seen_isbns = set()

    with httpx.Client(headers=HEADERS, follow_redirects=True, timeout=30) as client:
        print("Collecting Libris book URLs...")
        urls = collect_book_urls(client)
        print(f"\nTotal unique URLs: {len(urls)}\n")

        for i, url in enumerate(urls[:MAX_BOOKS]):
            short = url.split("/carte/")[-1][:55]
            print(f"[{i + 1}/{min(len(urls), MAX_BOOKS)}] {short}", end=" -> ")
            try:
                book = parse_book(client, url)
                if book:
                    if book["isbn"] and book["isbn"] in seen_isbns:
                        print("skip (dup)")
                        continue
                    if book["isbn"]:
                        seen_isbns.add(book["isbn"])
                    books.append(book)
                    print(f"OK  {book['title'][:50]}")
                else:
                    print("skip (no data)")
            except httpx.HTTPStatusError as exc:
                print(f"HTTP {exc.response.status_code}")
            except Exception as exc:
                print(f"error: {exc}")
            time.sleep(DELAY)

    OUTPUT_FILE.write_text(
        json.dumps(books, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"\nSaved {len(books)} books -> {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
