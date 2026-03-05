"""
Sample spider for Romanian book sources.
Uses a static list for MVP; replace with real crawl logic for production.
Respect robots.txt and rate limits.
"""
import scrapy
from crawler.items import BookItem


class SampleRomanianBooksSpider(scrapy.Spider):
    name = "sample_ro_books"
    custom_settings = {"ROBOTSTXT_OBEY": False}

    def start_requests(self):
        yield scrapy.Request("https://example.com", callback=self.parse, dont_filter=True)

    def parse(self, response):
        sample_books = [
            {
                "title": "Ion",
                "authors": ["Liviu Rebreanu"],
                "isbn": "9734601234",
                "publisher": "Editura pentru Literatură",
                "year": 1920,
            },
            {
                "title": "Enigma Otiliei",
                "authors": ["George Călinescu"],
                "isbn": "9732100123",
                "publisher": "Editura pentru Literatură",
                "year": 1938,
            },
            {
                "title": "Moromeții",
                "authors": ["Marin Preda"],
                "isbn": "9732100456",
                "publisher": "Cartea Românească",
                "year": 1955,
            },
        ]
        for b in sample_books:
            yield BookItem(**b)
