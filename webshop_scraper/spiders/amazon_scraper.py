import json
import re

from selectorlib import Extractor

from .webshop_scraper import WebshopScraper


class AmazonScraper(WebshopScraper):
    name = "amazon_scraper"

    # Proxy
    API_KEY = "9244ba171bff5bb2139d5403c443ee87"
    scraper_proxy = "http://scraperapi:{}@proxy-server.scraperapi.com:8001".format(API_KEY)

    # HTML extractor
    selector_file = 'webshop_scraper/amazon_selectors.yml'
    extractor = Extractor.from_yaml_file(selector_file)

    # HTML image regex
    image_pattern = re.compile(r'\'initial\': '
                               '(.*?)'
                               r'\},\n',
                               re.DOTALL)

    def __init__(self, n_pages=None, product_save_dir=None, scraped_urls_file=None, include_variants=True):
        super().__init__(n_pages=n_pages, product_save_dir=product_save_dir, scraped_urls_file=scraped_urls_file,
                         include_variants=include_variants)

    def get_start_urls(self):
        urls = [
            # "https://www.amazon.co.uk/s?rh=n%3A468292%2Cp_72%3A4-&pf_rd_i=468292&pf_rd_p=d40c144e-45ba-5915-b01d-d92bd82e9a59&pf_rd_r=9AHN48N59BT4GF71E1G8&pf_rd_s=merchandised-search-11&pf_rd_t=BROWSE", # toys
            # "https://www.amazon.co.uk/s?rh=n%3A117332031%2Cp_72%3A4-&pf_rd_i=117332031&pf_rd_p=4c8654cd-5980-5a4f-a532-3db1a3a6d579&pf_rd_r=AWW9M71158D9EAAAR8KB&pf_rd_s=merchandised-search-11&pf_rd_t=BROWSE", # beauty
            # "https://www.amazon.co.uk/s?i=sports&rh=n%3A461182031%2Cp_72%3A184323031&pf_rd_i=461182031&pf_rd_p=e9bb2e37-191c-532b-9180-73d951e30279&pf_rd_r=8R8CEN6NH34W6VM2610X&pf_rd_s=merchandised-search-11&pf_rd_t=BROWSE", # fit watches
            # "https://www.amazon.co.uk/s?rh=n%3A5866054031%2Cp_72%3A4-&pf_rd_i=5866054031&pf_rd_p=4ad30a04-262e-55f5-a315-4c86a63048cb&pf_rd_r=WTMSQNPE0Z6818GG7NMB&pf_rd_s=merchandised-search-11&pf_rd_t=BROWSE", # utilities / science
            # "https://www.amazon.com/s?i=specialty-aps&bbn=16225013011&rh=n%3A%2116225013011%2Cn%3A2975312011&ref=nav_em_0_2_14_2__nav_desktop_sa_intl_dogs", # dog
            # "https://www.amazon.co.uk/s?i=sports&rh=n%3A318949011%2Cp_72%3A184323031&pf_rd_i=318949011&pf_rd_p=b052e5ee-b3e8-5fa8-b467-a83cf0dcb513&pf_rd_r=JTXNEV8HM50Z5S18AEQ3&pf_rd_s=merchandised-search-11&pf_rd_t=BROWSE", # sports equipment
        ]

        return urls

    def get_product_pages(self, response):
        products = response.xpath("//span[@class='rush-component' and @data-component-type='s-product-image']").xpath(
            "a").xpath("@href").getall()
        products = ["/".join(url.split("/")[:4]) for url in products]
        products = [response.urljoin(url) for url in products]
        return products

    def get_product_info(self, response):
        html = response.text
        return self.extractor.extract(html)

    def get_product_image_urls(self, response):
        html = response.text
        try:
            data = self.image_pattern.search(html)
            images = data.group(1)
        except AttributeError:
            # no image carousel in page
            return []

        images = json.loads(images)
        images = [img["hiRes"] for img in images]
        return list(filter(None, images))

    def get_next_page_url(self, response):
        next_page_url = response.xpath("//ul[@class='a-pagination']/li[@class='a-last']/a").xpath("@href").get()
        next_page_url = response.urljoin(next_page_url)
        return next_page_url
