# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class Product(scrapy.Item):
    url = scrapy.Field()
    title = scrapy.Field()
    short_description = scrapy.Field()
    product_description = scrapy.Field()
    variant_type = scrapy.Field()
    variant_asins = scrapy.Field()
    image_urls = scrapy.Field()
    images = scrapy.Field()


class ProductVariant(scrapy.Item):
    product_url = scrapy.Field()
    name = scrapy.Field()
    asin = scrapy.Field()
    image_urls = scrapy.Field()
    images = scrapy.Field()