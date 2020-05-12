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
    no_of_pages = 1

    # To scrape product variants
    include_variants = True

    # Retry the request if encountering this page title
    retry_title = "Robot Check"

    # HTML extractor
    selector_file = 'webshop_scraper/selectors_product.yml'
    print(selector_file)
    extractor = Extractor.from_yaml_file(selector_file)

    # HTML image regex
    image_pattern = re.compile(r'\'initial\': '
                               '(.*?)'
                               r'\},\n',
                               re.DOTALL)

    # ScraperAPI
    API_KEY = "9244ba171bff5bb2139d5403c443ee87"
    scraper_proxy = "http://scraperapi:{}@proxy-server.scraperapi.com:8001".format(API_KEY)

    scraped_urls_file = "scraped_urls.txt"
    scraped_urls = load_scraped_urls(scraped_urls_file)
    product_save_dir = "data/products"

    headers = {
        'pragma': 'no-cache',
        'cache-control': 'no-cache',
        'dnt': '1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (X11; CrOS x86_64 8172.45.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.64 Safari/537.36',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
    }

    def start_requests(self):
        # starting urls for scraping
        urls = [
            "https://www.amazon.co.uk/s?rh=n%3A468292%2Cp_72%3A4-&pf_rd_i=468292&pf_rd_p=d40c144e-45ba-5915-b01d-d92bd82e9a59&pf_rd_r=9AHN48N59BT4GF71E1G8&pf_rd_s=merchandised-search-11&pf_rd_t=BROWSE"]

        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse, headers=self.headers, meta={"proxy": self.scraper_proxy})

    def parse(self, response):
        self.no_of_pages -= 1

        products = response.xpath("//span[@class='rush-component' and @data-component-type='s-product-image']").xpath(
            "a").xpath("@href").getall()
        products = ["/".join(url.split("/")[:4]) for url in products]
        print("Number of products on page:", len(products))

        for product in products:
            url = response.urljoin(product)
            if url not in self.scraped_urls:
                yield scrapy.Request(url=url, callback=self.parse_product, headers=self.headers,
                                     meta={"proxy": self.scraper_proxy})

        if (self.no_of_pages > 0):
            next_page_url = response.xpath("//ul[@class='a-pagination']/li[@class='a-last']/a").xpath("@href").get()
            url = response.urljoin(next_page_url)
            yield scrapy.Request(url=url, callback=self.parse, headers=self.headers)

    def parse_product(self, response):
        title = response.xpath("//span[@id='productTitle']//text()").get()
        print("TITLE:", title)

        url = response.url
        html = response.text

        images = self.extract_image_urls(html)
        data = self.extractor.extract(html)

        title = data["name"]
        short_desc = data["short_description"]
        prod_desc = data["product_description"]
        variants = data["variants"]
        variant_type = data["variant_type"]

        if self.include_variants and self.validate_variant(variant_type) and variants is not None:
            variant_asins = []
            for variant in variants:
                variant_suffix = variant["url_suffix"]
                if variant_suffix != "":
                    variant_asin = variant["asin"]
                    variant_asins.append(variant_asin)
                    variant_url = url + variant_suffix
                    yield scrapy.Request(variant_url, callback=self.parse_variant, headers=self.headers,
                                         meta={
                                             "product_url": url,
                                             "name": variant["name"],
                                             "asin": variant_asin,
                                             "proxy": self.scraper_proxy
                                         })
        else:
            variant_asins = None

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

        variant = ProductVariant(product_url=product_url, name=name, asin=asin, image_urls=image_urls)
        yield variant

    def validate_variant(self, variant_type):
        variant_type = str(variant_type).lower()

        if "color" in variant_type or "colour" in variant_type:
            return True

        return False

    def extract_image_urls(self, html):
        try:
            data = self.image_pattern.search(html)
            images = data.group(1)
        except AttributeError:
            print("No image carousel in page.")
            return []

        images = json.loads(images)
        images = [img["hiRes"] for img in images]
        return list(filter(None, images))
