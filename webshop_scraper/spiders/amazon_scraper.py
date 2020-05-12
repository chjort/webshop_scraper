import json
import re

import scrapy
from selectorlib import Extractor

from ..items import Product, ProductVariant


def load_scraped_urls(file):
    try:
        with open(file, "r") as f:
            urls = f.read().split("\n")
        return set(filter(None, urls))
    except FileNotFoundError:
        with open(file, "w") as f:
            pass
        return set()


class AmazonScraper(scrapy.Spider):
    name = "amazon_scraper"

    # How many pages you want to scrape
    n_pages = 1

    # To scrape product variants
    include_variants = True

    # Retry the request if encountering this page title
    retry_title = "Robot Check"

    # HTML extractor
    selector_file = 'webshop_scraper/amazon_selectors.yml'
    extractor = Extractor.from_yaml_file(selector_file)

    # HTML image regex
    image_pattern = re.compile(r'\'initial\': '
                               '(.*?)'
                               r'\},\n',
                               re.DOTALL)

    # ScraperAPI
    API_KEY = "9244ba171bff5bb2139d5403c443ee87"
    scraper_proxy = "http://scraperapi:{}@proxy-server.scraperapi.com:8001".format(API_KEY)

    #
    product_save_dir = "data/products"
    scraped_urls_file = "scraped_urls.txt"
    scraped_urls = load_scraped_urls(scraped_urls_file)

    #
    headers = {
        'pragma': 'no-cache',
        'cache-control': 'no-cache',
        'dnt': '1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (X11; CrOS x86_64 8172.45.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.64 Safari/537.36',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
    }

    def __init__(self, n_pages=None, product_save_dir=None, scraped_urls_file=None):
        super().__init__(name=self.name)
        if n_pages is not None:
            self.n_pages = n_pages
        if product_save_dir is not None:
            self.product_save_dir = product_save_dir
        if scraped_urls_file is not None:
            self.scraped_urls_file = scraped_urls_file

    def start_requests(self):
        # starting urls for scraping
        urls = [
            # "https://www.amazon.co.uk/s?rh=n%3A468292%2Cp_72%3A4-&pf_rd_i=468292&pf_rd_p=d40c144e-45ba-5915-b01d-d92bd82e9a59&pf_rd_r=9AHN48N59BT4GF71E1G8&pf_rd_s=merchandised-search-11&pf_rd_t=BROWSE",
            # "https://www.amazon.co.uk/s?rh=n%3A117332031%2Cp_72%3A4-&pf_rd_i=117332031&pf_rd_p=4c8654cd-5980-5a4f-a532-3db1a3a6d579&pf_rd_r=AWW9M71158D9EAAAR8KB&pf_rd_s=merchandised-search-11&pf_rd_t=BROWSE",
            "https://www.amazon.co.uk/s?i=sports&rh=n%3A461182031%2Cp_72%3A184323031&pf_rd_i=461182031&pf_rd_p=e9bb2e37-191c-532b-9180-73d951e30279&pf_rd_r=8R8CEN6NH34W6VM2610X&pf_rd_s=merchandised-search-11&pf_rd_t=BROWSE"
        ]

        for url in urls:
            yield self.proxy_request(url, callback=self.parse, meta={"n_pages_to_scrape": self.n_pages})

    def parse(self, response):
        products = response.xpath("//span[@class='rush-component' and @data-component-type='s-product-image']").xpath(
            "a").xpath("@href").getall()
        products = ["/".join(url.split("/")[:4]) for url in products]

        self.logger.info("Crawling {}".format(response.url))
        self.logger.info("Number of products on page: {}".format(len(products)))

        for product in products:
            url = response.urljoin(product)
            if url not in self.scraped_urls:
                yield self.proxy_request(url, callback=self.parse_product)

        n_pages_to_scrape = response.meta["n_pages_to_scrape"]
        n_pages_to_scrape = n_pages_to_scrape - 1
        if n_pages_to_scrape > 0:
            next_page_url = response.xpath("//ul[@class='a-pagination']/li[@class='a-last']/a").xpath("@href").get()
            url = response.urljoin(next_page_url)
            yield self.proxy_request(url, callback=self.parse, meta={"n_pages_to_scrape": n_pages_to_scrape})

    def parse_product(self, response):
        url = response.url
        html = response.text

        data = self.extractor.extract(html)
        title = data["name"]
        short_desc = data["short_description"]
        prod_desc = data["product_description"]
        variants = data["variants"]
        variant_type = data["variant_type"]

        self.logger.info("TITLE: {}".format(title))

        images = self.extract_image_urls(html)
        self.logger.info("images: {}".format(len(images)))

        if self.include_variants and self.validate_variant(variant_type) and variants is not None:
            variant_asins = []
            for variant in variants:
                variant_suffix = variant["url_suffix"]
                if variant_suffix != "":
                    variant_asin = variant["asin"]
                    variant_asins.append(variant_asin)
                    variant_url = url + variant_suffix
                    yield self.proxy_request(variant_url, callback=self.parse_variant,
                                             meta={
                                                 "product_url": url,
                                                 "title": title,
                                                 "name": variant["name"],
                                                 "asin": variant_asin,
                                             })
            self.logger.info("variants: {}".format(len(variant_asins)))
        else:
            variant_asins = None
            self.logger.info("variants: {}".format(variant_asins))

        product = Product(title=title,
                          short_description=short_desc,
                          product_description=prod_desc,
                          variant_type=variant_type,
                          variant_asins=variant_asins,
                          image_urls=images,
                          url=url
                          )

        yield product

    def parse_variant(self, response):
        html = response.text

        product_url = response.meta["product_url"]
        name = response.meta["name"]
        asin = response.meta["asin"]
        image_urls = self.extract_image_urls(html)

        product_title = response.meta["title"]
        self.logger.info("Variant {}-{}: {} images".format(asin, product_title, len(image_urls)))

        variant = ProductVariant(product_url=product_url, name=name, asin=asin, image_urls=image_urls)
        yield variant

    def proxy_request(self, url, callback, meta=None):
        if meta is not None:
            meta["proxy"] = self.scraper_proxy
        else:
            meta = {"proxy": self.scraper_proxy}

        return self.request(url, callback, meta)

    def request(self, url, callback, meta=None):
        return scrapy.Request(url=url, callback=callback, headers=self.headers, meta=meta)

    def extract_image_urls(self, html):
        try:
            data = self.image_pattern.search(html)
            images = data.group(1)
        except AttributeError:
            # no image carousel in page
            return []

        images = json.loads(images)
        images = [img["hiRes"] for img in images]
        return list(filter(None, images))

    @staticmethod
    def validate_variant(variant_type):
        variant_type = str(variant_type).lower()

        if "color" in variant_type or "colour" in variant_type:
            return True

        return False
