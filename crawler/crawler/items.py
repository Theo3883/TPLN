import scrapy


class BookItem(scrapy.Item):
    title = scrapy.Field()
    authors = scrapy.Field()
    isbn = scrapy.Field()
    publisher = scrapy.Field()
    year = scrapy.Field()
    source_url = scrapy.Field()
