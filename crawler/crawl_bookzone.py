"""
Bookzone.ro crawler — BeautifulSoup + httpx.

Strategy:
  1. Fetch the product sitemap (SitemapProduseNoi.aspx) for /carte/ URLs.
  2. Visit each detail page and extract metadata from JSON-LD.

Output: output/bookzone.json
"""
from __future__ import annotations

import json
import re
import time
import xml.etree.ElementTree as ET
from pathlib import Path

import httpx
from bs4 import BeautifulSoup

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
OUTPUT_DIR = Path(__file__).parent / "output"
OUTPUT_FILE = OUTPUT_DIR / "bookzone.json"

SITEMAP_URLS = [
    "https://bookzone.ro/sitemaps-g/SitemapProduseNoi.aspx",
    "https://bookzone.ro/sitemaps-g/SitemapProduse.aspx",
]
DELAY = 3          # seconds between requests
MAX_BOOKS = 200    # stop after this many books

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (compatible; LitPlatformBot/1.0; educational project)"
    ),
}

NS = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def normalize_isbn(raw):
    """Keep only digits; accept 10- or 13-digit ISBNs."""
    if not raw:
        return None
    digits = "".join(c for c in str(raw) if c.isdigit())
    return digits if len(digits) in (10, 13) else None


def parse_year(raw):
    if not raw:
        return None
    m = re.search(r"\b(19|20)\d{2}\b", str(raw))
    return int(m.group()) if m else None


def _clean_json_string(raw):
    """Remove / replace control characters that break json.loads."""
    if not raw:
        return ""
    # Replace all ASCII control chars (including \n \r \t inside strings)
    # with a space — JSON-LD is typically single-line anyway.
    return re.sub(r"[\x00-\x1f]+", " ", raw)


def extract_json_ld_product(soup):
    """Return the first JSON-LD object whose @type includes Product or Book."""
    decoder = json.JSONDecoder()
    for script in soup.find_all("script", type="application/ld+json"):
        raw = script.string
        if not raw:
            raw = script.get_text()
        if not raw:
            continue
        raw = _clean_json_string(raw).strip()

        # Try parsing — may contain multiple JSON objects concatenated
        pos = 0
        while pos < len(raw):
            try:
                data, end = decoder.raw_decode(raw, pos)
            except json.JSONDecodeError:
                break
            items = data if isinstance(data, list) else [data]
            for item in items:
                t = item.get("@type", "")
                types = t if isinstance(t, list) else [t]
                if "Product" in types or "Book" in types:
                    return item
            pos = end
            # Skip whitespace between concatenated objects
            while pos < len(raw) and raw[pos] in " \t\n\r":
                pos += 1
    return None


def _extract_isbn_from_scripts(soup):
    """Find ISBN embedded in inline JS (e.g. Bookzone Nuxt data)."""
    for script in soup.find_all("script"):
        text = script.string or ""
        m = re.search(r'"isbn"\s*:\s*"(\d{10,13})"', text)
        if m:
            return m.group(1)
    return None


# ---------------------------------------------------------------------------
# Sitemap
# ---------------------------------------------------------------------------
def get_book_urls(client):
    """Fetch sitemap(s) and collect /carte/ URLs."""
    urls = []
    seen = set()
    for sitemap_url in SITEMAP_URLS:
        try:
            r = client.get(sitemap_url)
            r.raise_for_status()
            root = ET.fromstring(r.text)
            for loc in root.findall(".//sm:loc", NS):
                url = (loc.text or "").strip()
                if "/carte/" in url and url not in seen:
                    seen.add(url)
                    urls.append(url)
            print(f"  {sitemap_url} -> {len(urls)} book URLs so far")
        except Exception as e:
            print(f"  {sitemap_url} -> error: {e}")
    return urls


# ---------------------------------------------------------------------------
# Detail page
# ---------------------------------------------------------------------------
def parse_book(client, url):
    r = client.get(url)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")

    ld = extract_json_ld_product(soup)

    if ld:
        # --- Extract from JSON-LD ---
        title = (ld.get("name") or "").strip()
        isbn = normalize_isbn(ld.get("isbn") or ld.get("gtin13"))
        pub = ld.get("publisher", "")
        if isinstance(pub, dict):
            pub = pub.get("name", "")
        publisher = pub.strip() or None
        year = parse_year(ld.get("datePublished"))

        raw = ld.get("author", "")
        if isinstance(raw, str):
            authors = [a.strip() for a in raw.split(",") if a.strip()]
        elif isinstance(raw, list):
            authors = [
                (a["name"].strip() if isinstance(a, dict) else str(a).strip())
                for a in raw
            ]
        elif isinstance(raw, dict):
            authors = [raw.get("name", "").strip()]
        else:
            authors = []

        # Supplement: when JSON-LD has no author, the first /autor/
        # link with a *relative* href is typically the book's author.
        if not authors:
            for tag in soup.find_all("a", href=re.compile(r"^/autor/")):
                name = tag.get_text(strip=True)
                if (name and not name.startswith("Carti ")
                        and "Vezi pagina" not in name
                        and name not in authors):
                    authors.append(name)
                    break  # only take the first one to avoid sidebar noise
    else:
        # No JSON-LD at all — extract from h1 + inline scripts only.
        # /autor/ links are sidebar "popular authors", NOT the book's author.
        title = ""
        isbn = None
        publisher = None
        year = None
        authors = []
    # --- Supplement from HTML ---
    if not title:
        h1 = soup.find("h1")
        title = h1.get_text(strip=True) if h1 else ""
    if not title:
        return None

    if not isbn:
        isbn = normalize_isbn(_extract_isbn_from_scripts(soup))

    if not publisher:
        # Only first relative /editura/ link — later ones are sidebar
        tag = soup.find("a", href=re.compile(r"^/editura/"))
        if tag:
            publisher = tag.get_text(strip=True)

    # Image
    img = (ld.get("image") or "") if ld else ""
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
        print("Fetching Bookzone sitemaps...")
        urls = get_book_urls(client)
        print(f"Total book URLs: {len(urls)}\n")

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
