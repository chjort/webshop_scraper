import abc

import scrapy

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


class WebshopScraper(scrapy.Spider, abc.ABC):
    name = "webshop_scraper"

    # Proxy
    scraper_proxy = None

    # headers
    headers = {
        'pragma': 'no-cache',
        'cache-control': 'no-cache',
        'dnt': '1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (X11; CrOS x86_64 8172.45.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.64 Safari/537.36',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
    }

    def __init__(self, n_pages=1, product_save_dir=None, scraped_urls_file=None, include_variants=True):
        super().__init__(name=self.name)
        self.n_pages = n_pages  # How many pages you want to scrape

        # IO
        if product_save_dir is None:
            self.product_save_dir = "data/{}".format(self.name)
        else:
            self.product_save_dir = product_save_dir

        if scraped_urls_file is None:
            self.scraped_urls_file = "{}_scraped_urls.txt".format(self.name)
        else:
            self.scraped_urls_file = scraped_urls_file

        self.scraped_urls = load_scraped_urls(self.scraped_urls_file)
        self.include_variants = include_variants

    def start_requests(self):
        # starting urls for scraping
        urls = self.get_start_urls()

        for url in urls:
            yield self.proxy_request(url, callback=self.parse, meta={"n_pages_to_scrape": self.n_pages})

    def parse(self, response):
        self.logger.info("Crawling {}".format(response.url))

        products = self.get_product_pages(response)
        self.logger.info("Number of products on page: {}".format(len(products)))

        for url in products:
            if url not in self.scraped_urls:
                yield self.proxy_request(url, callback=self.parse_product)

        n_pages_to_scrape = response.meta["n_pages_to_scrape"]
        n_pages_to_scrape = n_pages_to_scrape - 1
        if n_pages_to_scrape > 0:
            next_url = self.get_next_page_url(response)
            yield self.proxy_request(next_url, callback=self.parse, meta={"n_pages_to_scrape": n_pages_to_scrape})

    def parse_product(self, response):
        url = response.url

        data = self.get_product_info(response)
        title = data.get("name")
        short_desc = data.get("short_description")
        prod_desc = data.get("product_description")
        variants = data.get("variants")
        variant_type = data.get("variant_type")

        self.logger.info("TITLE: {}".format(title))

        images = self.get_product_image_urls(response)
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
        product_url = response.meta["product_url"]
        name = response.meta["name"]
        asin = response.meta["asin"]
        image_urls = self.get_product_image_urls(response)

        product_title = response.meta["title"]
        self.logger.info("Variant {}-{}: {} images".format(asin, product_title, len(image_urls)))

        variant = ProductVariant(product_url=product_url, name=name, asin=asin, image_urls=image_urls)
        yield variant

    def proxy_request(self, url, callback, meta=None):
        if self.scraper_proxy is not None:
            if meta is not None:
                meta["proxy"] = self.scraper_proxy
            else:
                meta = {"proxy": self.scraper_proxy}

        return self.request(url, callback, meta)

    def request(self, url, callback, meta=None):
        return scrapy.Request(url=url, callback=callback, headers=self.headers, meta=meta)

    @staticmethod
    def validate_variant(variant_type):
        if variant_type is None:
            return False

        variant_type = str(variant_type).lower()
        if "color" in variant_type or "colour" in variant_type:
            return True

        return False

    @abc.abstractmethod
    def get_start_urls(self):
        pass

    @abc.abstractmethod
    def get_product_pages(self, response):
        pass

    @abc.abstractmethod
    def get_product_info(self, response):
        pass

    @abc.abstractmethod
    def get_product_image_urls(self, response):
        pass

    @abc.abstractmethod
    def get_next_page_url(self, response):
        pass
