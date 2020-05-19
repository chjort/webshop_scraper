import datetime
import os

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from webshop_scraper.spiders.amazon_scraper import AmazonScraper
from webshop_scraper.spiders.br_scraper import BRScraper

crawl_time = int(datetime.datetime.now().timestamp())
# amz_save_dir = os.path.join("data", AmazonScraper.name + "_" + str(crawl_time))
br_save_dir = os.path.join("data", BRScraper.name + "_" + str(crawl_time))

settings = get_project_settings()
process = CrawlerProcess(settings=settings)
# process.crawl(AmazonScraper, n_pages=50, product_save_dir=amz_save_dir)
process.crawl(BRScraper, n_pages=200, product_save_dir=br_save_dir)
process.start()
