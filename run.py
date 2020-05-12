from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from webshop_scraper.spiders.amazon_scraper import AmazonScraper

settings = get_project_settings()
process = CrawlerProcess(settings=settings)
process.crawl(AmazonScraper)
process.start()
