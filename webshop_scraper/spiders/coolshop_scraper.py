from .webshop_scraper import WebshopScraper


class CoolshopScraper(WebshopScraper):
    name = "coolshop_scraper"

    def __init__(self, n_pages=None, product_save_dir=None, scraped_urls_file=None, include_variants=True):
        super().__init__(n_pages=n_pages, product_save_dir=product_save_dir, scraped_urls_file=scraped_urls_file,
                         include_variants=include_variants)

    def get_start_urls(self):
        urls = [
            "https://www.coolshop.dk/s/"
        ]

        return urls

    def get_product_pages(self, response):
        products = response.xpath("//div[@class='product-cards__thumbnail']").xpath(
            "a").xpath("@href").getall()
        products = [response.urljoin(url) for url in products]
        return products

    def get_product_info(self, response):
        pass

    def get_product_image_urls(self, response):
        pass

    def get_next_page_url(self, response):
        pass
