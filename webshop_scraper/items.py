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

    def __repr__(self):
        repstr = "{}: {} images".format(self["title"], len(self["image_urls"]))
        return repstr


class ProductVariant(scrapy.Item):
    product_url = scrapy.Field()
    name = scrapy.Field()
    asin = scrapy.Field()
    image_urls = scrapy.Field()
    images = scrapy.Field()

    def __repr__(self):
        reprstr = "{}: {} images".format(self["asin"], len(self["image_urls"]))
        return reprstr
