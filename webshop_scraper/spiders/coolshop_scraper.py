from selectorlib import Extractor

from .webshop_scraper import WebshopScraper


class CoolshopScraper(WebshopScraper):
    name = "coolshop_scraper"

    # HTML extractor
    selector_file = 'webshop_scraper/coolshop_selectors.yml'
    extractor = Extractor.from_yaml_file(selector_file)

    def __init__(self, n_pages=None, product_save_dir=None, scraped_urls_file=None, include_variants=True):
        super().__init__(n_pages=n_pages, product_save_dir=product_save_dir, scraped_urls_file=scraped_urls_file,
                         include_variants=include_variants)

    def get_start_urls(self):
        urls = [
            "https://www.coolshop.dk/s/"
        ]

        return urls

    def get_product_pages(self, response):
        # products = response.xpath("//div[@class='product-cards__thumbnail']").xpath(
        #     "a").xpath("@href").getall()
        products = response.xpath("//div[@class='product-cards__thumbnail']//a//@href").getall()
        products = [response.urljoin(url) for url in products if "l-o-l" not in url]
        return products

    def get_product_info(self, response):
        html = response.text
        data = self.extractor.extract(html)
        return data

    def get_product_image_urls(self, response):
        image_urls = response.xpath("//div[@class='thing-media-list']//li//a[@data-type='image']//@href").getall()
        return image_urls

    def get_next_page_url(self, response):
        pass
