from .webshop_scraper import WebshopScraper


class BRScraper(WebshopScraper):
    name = "br_scraper"

    # Proxy
    # API_KEY = "9244ba171bff5bb2139d5403c443ee87"
    # scraper_proxy = "http://scraperapi:{}@proxy-server.scraperapi.com:8001".format(API_KEY)

    def __init__(self, n_pages=None, product_save_dir=None, scraped_urls_file=None, include_variants=True):
        super().__init__(n_pages=n_pages, product_save_dir=product_save_dir, scraped_urls_file=scraped_urls_file,
                         include_variants=include_variants)

    def get_start_urls(self):
        urls = [
            "https://www.br.dk/search?q=*&f=categories%3D3-4%20%C3%A5r%3Acategories%3D5-6%20%C3%A5r%3Acategories%3D7-8%20%C3%A5r%3Acategories%3D9-10%20%C3%A5r%3Acategories%3DBygges%C3%A6t%3Acategories%3DKonstruktionsleget%C3%B8j%3Acategories%3DKreativitet%3Acategories%3DLeget%C3%B8j%3Acategories%3DUdend%C3%B8rs%20leg"
        ]

        return urls

    def get_product_pages(self, response):
        products_suffixes = response.xpath("//div[@class='pf_title']//a//@href").getall()
        products = [response.urljoin(suffix) for suffix in products_suffixes]
        return products

    def get_product_info(self, response):
        title = response.xpath("//h1[@class='bilka_main_heading fn']//text()").get()
        short_description = response.xpath("//h2[@class='bilka-h2']//text()").get()
        description = response.xpath("//div[@id='desc-more']//p//text()").getall()
        description = "\n".join(description)
        data = {"name": title, "short_description": short_description,
                "product_description": description, "variants": None,
                "variant_type": None}
        return data

    def get_product_image_urls(self, response):
        imgs = response.xpath("//li[@data-media_big]//@data-media_big").getall()
        imgs = [img_url for img_url in imgs if img_url.startswith("http")]
        return imgs

    def get_next_page_url(self, response):
        next_page_url = response.xpath("//a[@class='lt_pager next']//@href").get()
        next_page_url = response.urljoin(next_page_url)
        return next_page_url
