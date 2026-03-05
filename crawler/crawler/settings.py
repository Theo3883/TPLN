BOT_NAME = "crawler"
SPIDER_MODULES = ["crawler.spiders"]
NEWSPIDER_MODULE = "crawler.spiders"
ROBOTSTXT_OBEY = True
REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"
CONCURRENT_REQUESTS = 2
DOWNLOAD_DELAY = 2
ITEM_PIPELINES = {
    "crawler.pipelines.NormalizePipeline": 100,
    "crawler.pipelines.DeduplicatePipeline": 200,
    "crawler.pipelines.StorePipeline": 300,
}
API_BASE_URL = "http://localhost:8000"
