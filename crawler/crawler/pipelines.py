import re
import httpx
from scrapy import Spider

from crawler.items import BookItem


def normalize_isbn(value):
    if not value:
        return None
    digits = "".join(c for c in str(value) if c.isdigit())
    if len(digits) in (10, 13):
        return digits
    return None


def normalize_title(value):
    if not value:
        return ""
    return " ".join(str(value).strip().split())


def normalize_author(name):
    if not name:
        return ""
    return " ".join(str(name).strip().split())


def parse_year(value):
    if not value:
        return None
    m = re.search(r"\b(19|20)\d{2}\b", str(value))
    return int(m.group(0)) if m else None


class NormalizePipeline:
    def process_item(self, item, spider: Spider):
        if not isinstance(item, BookItem):
            return item
        item["title"] = normalize_title(item.get("title"))
        item["authors"] = [normalize_author(a) for a in item.get("authors", []) if a]
        item["isbn"] = normalize_isbn(item.get("isbn"))
        item["publisher"] = normalize_title(item.get("publisher")) or None
        item["year"] = parse_year(item.get("year"))
        return item


class DeduplicatePipeline:
    def __init__(self, api_url):
        self.api_url = api_url
        self.seen_isbns = set()

    @classmethod
    def from_crawler(cls, crawler):
        return cls(api_url=crawler.settings.get("API_BASE_URL", "http://localhost:8000"))

    def process_item(self, item, spider: Spider):
        if not isinstance(item, BookItem):
            return item
        if item.get("isbn") and item["isbn"] in self.seen_isbns:
            spider.logger.info(f"Dedup skip ISBN {item['isbn']}")
            return None
        if item.get("isbn"):
            self.seen_isbns.add(item["isbn"])
        return item


class StorePipeline:
    def __init__(self, api_url):
        self.api_url = api_url

    @classmethod
    def from_crawler(cls, crawler):
        return cls(api_url=crawler.settings.get("API_BASE_URL", "http://localhost:8000"))

    def process_item(self, item, spider: Spider):
        if not isinstance(item, BookItem):
            return item
        if not item.get("title"):
            return None
        payload = {
            "title": item["title"],
            "authors": item.get("authors", []),
            "isbn": item.get("isbn"),
            "publisher": item.get("publisher"),
            "year": item.get("year"),
        }
        with httpx.Client(timeout=30) as client:
            r = client.post(f"{self.api_url}/ingest", json=payload)
            if r.status_code == 200:
                data = r.json()
                spider.logger.info(f"Stored: {data.get('status')} edition_id={data.get('edition_id')}")
            else:
                spider.logger.warning(f"Store failed {r.status_code}: {r.text}")
        return item
