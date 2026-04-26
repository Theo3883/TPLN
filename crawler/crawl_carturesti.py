"""
Carturesti.ro crawler — BeautifulSoup + httpx.

Carturesti is an AngularJS SPA: listing pages don't contain book data in
static HTML.  This crawler uses three strategies (in order) to discover
book URLs:

  1. Internal AJAX filter endpoint found on /raft/ pages.
  2. The /product/simple-search endpoint for keyword queries.
  3. The XML sitemap as a last-resort fallback.

Detail pages are also SPA-rendered, so metadata is extracted from whatever
is available: JSON-LD (if present), <a href="/autor/"> links, <a href="/editura/">
links, and the URL slug as a title fallback.

Output: output/carturesti.json
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
OUTPUT_FILE = OUTPUT_DIR / "carturesti.json"

BASE_URL = "https://carturesti.ro"
RAFT_URLS = [
    f"{BASE_URL}/raft/carte-109",
    f"{BASE_URL}/raft/carte-straina-1937",
]
SITEMAP_URL = f"{BASE_URL}/sitemap.xml"
DELAY = 3
MAX_BOOKS = 200

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
    if not raw:
        return None
    digits = "".join(c for c in str(raw) if c.isdigit())
    return digits if len(digits) in (10, 13) else None


def parse_year(raw):
    if not raw:
        return None
    m = re.search(r"\b(19|20)\d{2}\b", str(raw))
    return int(m.group()) if m else None


def _get_csrf(soup):
    meta = soup.find("meta", attrs={"name": "csrf-token"})
    return meta["content"] if meta else ""


def _full_url(href):
    if href.startswith("http"):
        return href
    return BASE_URL + href


# ---------------------------------------------------------------------------
# Strategy 1 — AJAX filter endpoints from /raft/ pages
# ---------------------------------------------------------------------------
def discover_via_ajax(client):
    """
    Visit each raft page, find the Angular init params that contain
    a 'fid' and a '/ajax-filter' URL, then POST to that endpoint
    with offset/limit to retrieve product HTML fragments.
    """
    book_urls = []
    seen = set()

    for raft_url in RAFT_URLS:
        raft_name = raft_url.split("/raft/")[-1]
        print(f"  Raft: {raft_name}")
        try:
            r = client.get(raft_url)
            r.raise_for_status()
        except Exception as e:
            print(f"    error fetching raft page: {e}")
            continue

        soup = BeautifulSoup(r.text, "html.parser")
        csrf = _get_csrf(soup)

        # Extract {"fid": NNN, "url": "/ajax-filter?id=NNN&id_weight=0"}
        filter_pairs = re.findall(
            r'"fid"\s*:\s*(\d+)[^}]*?"url"\s*:\s*"([^"]+)"',
            r.text,
        )
        if not filter_pairs:
            print("    no filter endpoints found")
            time.sleep(DELAY)
            continue

        print(f"    {len(filter_pairs)} filter endpoint(s)")

        for fid, raw_url in filter_pairs:
            clean_path = raw_url.replace("\\/", "/").replace("\\", "")
            endpoint = _full_url(clean_path)

            # POST with the same shape the Angular loadProducts() uses
            for offset in range(0, 200, 40):
                body = {
                    "offset": offset,
                    "limit": 40,
                    "fid": int(fid),
                    "overwrite": [],
                    "url": clean_path,
                }
                try:
                    resp = client.post(
                        endpoint,
                        json=body,
                        headers={
                            "X-Requested-With": "XMLHttpRequest",
                            "X-CSRF-Token": csrf,
                            "Accept": "text/html, application/json, */*",
                            "Referer": raft_url,
                        },
                    )
                    if resp.status_code != 200:
                        break

                    ct = resp.headers.get("content-type", "")
                    new_count = 0

                    if "json" in ct:
                        data = resp.json()
                        products = []
                        if isinstance(data, dict):
                            products = data.get("products", data.get("items", []))
                        elif isinstance(data, list):
                            products = data
                        for p in products:
                            if isinstance(p, dict):
                                href = (
                                    p.get("url")
                                    or p.get("href")
                                    or p.get("link")
                                    or ""
                                )
                                if href and "/carte/" in href:
                                    full = _full_url(href.split("?")[0])
                                    if full not in seen:
                                        seen.add(full)
                                        book_urls.append(full)
                                        new_count += 1
                    else:
                        # HTML fragment — parse for /carte/ links
                        frag = BeautifulSoup(resp.text, "html.parser")
                        for a in frag.find_all("a", href=re.compile(r"/carte/")):
                            href = a["href"].split("?")[0]
                            full = _full_url(href)
                            if full not in seen:
                                seen.add(full)
                                book_urls.append(full)
                                new_count += 1

                    if new_count == 0:
                        break  # no more products at this offset
                    print(f"    offset={offset}: +{new_count} URLs")

                except Exception as e:
                    print(f"    POST error: {e}")
                    break

                time.sleep(DELAY)

            # Also try GET on the same endpoint
            try:
                resp_get = client.get(
                    endpoint,
                    headers={
                        "X-Requested-With": "XMLHttpRequest",
                        "Accept": "text/html, application/json, */*",
                        "Referer": raft_url,
                    },
                )
                if resp_get.status_code == 200:
                    frag = BeautifulSoup(resp_get.text, "html.parser")
                    for a in frag.find_all("a", href=re.compile(r"/carte/")):
                        href = a["href"].split("?")[0]
                        full = _full_url(href)
                        if full not in seen:
                            seen.add(full)
                            book_urls.append(full)
            except Exception:
                pass

            time.sleep(DELAY)

        time.sleep(DELAY)

    return book_urls


# ---------------------------------------------------------------------------
# Strategy 2 — /product/simple-search
# ---------------------------------------------------------------------------
SEARCH_TERMS = [
    "roman", "poezie", "istorie", "fictiune", "psihologie",
    "copii", "educatie", "stiinta", "filosofie", "arta",
    "literatura", "matematica", "biologie", "chimie", "fizica",
]


def discover_via_search(client, already_found):
    """Try the internal search endpoint with various keywords."""
    seen = set(already_found)
    new_urls = []

    for term in SEARCH_TERMS:
        try:
            r = client.get(
                f"{BASE_URL}/product/simple-search",
                params={"q": term},
                headers={
                    "X-Requested-With": "XMLHttpRequest",
                    "Accept": "application/json",
                },
            )
            if r.status_code != 200:
                continue

            ct = r.headers.get("content-type", "")
            if "json" not in ct:
                continue

            data = r.json()
            items = []
            if isinstance(data, list):
                items = data
            elif isinstance(data, dict):
                items = data.get("products", data.get("items", data.get("results", [])))

            count = 0
            for item in items:
                if not isinstance(item, dict):
                    continue
                # Try various keys for the URL or slug
                href = item.get("url") or item.get("href") or item.get("link") or ""
                slug = item.get("slug") or item.get("alias") or ""
                pid = item.get("id") or item.get("productId") or ""

                if href and "/carte/" in href:
                    full = _full_url(href.split("?")[0])
                elif slug:
                    full = f"{BASE_URL}/carte/{slug}"
                elif pid:
                    full = f"{BASE_URL}/carte/{pid}"
                else:
                    continue

                if full not in seen:
                    seen.add(full)
                    new_urls.append(full)
                    count += 1

            if count:
                print(f"    '{term}': +{count} URLs")

        except Exception:
            pass  # search is best-effort
        time.sleep(DELAY)

    return new_urls


# ---------------------------------------------------------------------------
# Strategy 3 — XML sitemap fallback
# ---------------------------------------------------------------------------
def discover_via_sitemap(client, already_found):
    seen = set(already_found)
    new_urls = []
    try:
        r = client.get(SITEMAP_URL)
        r.raise_for_status()
        root = ET.fromstring(r.text)
        for loc in root.findall(".//sm:loc", NS):
            url = (loc.text or "").strip()
            if "/carte/" in url and url not in seen:
                seen.add(url)
                new_urls.append(url)
        print(f"    sitemap: +{len(new_urls)} URLs")
    except Exception as e:
        print(f"    sitemap error: {e}")
    return new_urls


# ---------------------------------------------------------------------------
# Detail page parsing
# ---------------------------------------------------------------------------
def _extract_json_ld(soup):
    for script in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(script.string)
            items = data if isinstance(data, list) else [data]
            for item in items:
                t = item.get("@type", "")
                types = t if isinstance(t, list) else [t]
                if "Product" in types or "Book" in types:
                    return item
        except (json.JSONDecodeError, TypeError):
            continue
    return None


def _title_from_slug(url):
    """Last resort: derive a readable title from the URL slug."""
    m = re.search(r"/carte/([^/]+?)(?:-(\d{4,}))?\s*$", url)
    if not m:
        return ""
    slug = m.group(1)
    words = slug.split("-")
    # Remove trailing numeric id if present
    if words and words[-1].isdigit():
        words = words[:-1]
    return " ".join(w.capitalize() for w in words)


def parse_book(client, url):
    r = client.get(url)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")

    ld = _extract_json_ld(soup)

    # --- Try JSON-LD first ---
    if ld:
        title = (ld.get("name") or "").strip()
        isbn = normalize_isbn(
            ld.get("isbn") or ld.get("gtin13") or ld.get("GTIN13")
        )
        pub = ld.get("publisher") or ld.get("brand") or ""
        if isinstance(pub, dict):
            pub = pub.get("name", "")
        publisher = pub.strip() or None
        year = parse_year(ld.get("datePublished"))

        raw_auth = ld.get("author", "")
        if isinstance(raw_auth, str):
            authors = [a.strip() for a in raw_auth.split(",") if a.strip()]
        elif isinstance(raw_auth, list):
            authors = [
                (a["name"].strip() if isinstance(a, dict) else str(a).strip())
                for a in raw_auth
            ]
        elif isinstance(raw_auth, dict):
            authors = [raw_auth.get("name", "").strip()]
        else:
            authors = []
    else:
        title = ""
        isbn = None
        publisher = None
        year = None
        authors = []

    # --- Supplement from HTML ---
    if not title:
        h1 = soup.find("h1")
        if h1:
            title = h1.get_text(strip=True)
    if not title:
        og = soup.find("meta", property="og:title")
        if og:
            t = og.get("content", "")
            # Reject the generic fallback title
            if t and t.lower() not in ("carturesti.ro", "cărturești.ro"):
                title = t
    if not title:
        title = _title_from_slug(url)
    if not title:
        return None

    if not authors:
        for tag in soup.find_all("a", href=re.compile(r"/autor/")):
            name = tag.get_text(strip=True)
            if name and name not in authors:
                authors.append(name)

    if not publisher:
        for tag in soup.find_all("a", href=re.compile(r"/editura/")):
            text = tag.get_text(strip=True)
            if text and text.lower() != "vezi mai multe":
                publisher = text
                break

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
        # Strategy 1
        print("Strategy 1: AJAX filter endpoints...")
        urls = discover_via_ajax(client)
        print(f"  total: {len(urls)} URLs\n")

        # Strategy 2
        if len(urls) < MAX_BOOKS:
            print("Strategy 2: search endpoint...")
            urls += discover_via_search(client, urls)
            print(f"  total: {len(urls)} URLs\n")

        # Strategy 3
        if len(urls) < MAX_BOOKS:
            print("Strategy 3: sitemap fallback...")
            urls += discover_via_sitemap(client, urls)
            print(f"  total: {len(urls)} URLs\n")

        # Deduplicate (preserve order)
        urls = list(dict.fromkeys(urls))[:MAX_BOOKS]
        print(f"Fetching {len(urls)} book pages...\n")

        for i, url in enumerate(urls):
            short = url.split("/carte/")[-1][:55] if "/carte/" in url else url[-55:]
            print(f"[{i + 1}/{len(urls)}] {short}", end=" -> ")
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
