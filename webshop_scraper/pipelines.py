# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


import hashlib
import json
import os
import shutil

from scrapy.utils.python import to_bytes

from .items import Product, ProductVariant


class ProductPipeline:
    def open_spider(self, spider):
        self.scraped_urls_file = open(spider.scraped_urls_file, "a")
        self.output_dir = spider.product_save_dir
        self.image_folder = spider.settings.get("IMAGES_STORE")
        os.makedirs(self.output_dir, exist_ok=True)
        self.min_images = 2

    def process_item(self, item, spider):
        images = item["images"]
        image_names = [img["path"] for img in images]

        if isinstance(item, Product):
            prod_url = item["url"]
            if len(image_names) < self.min_images:
                self.scraped_urls_file.write(prod_url + "\n")
                return item
            new_image_names = ["0_" + os.path.basename(name) for name in image_names]
            info = {"title": item["title"],
                    "short_description": item["short_description"],
                    "product_description": item["product_description"],
                    }
        elif isinstance(item, ProductVariant):
            prod_url = item["product_url"]
            if len(image_names) < self.min_images:
                return item
            asin = item["asin"]
            new_image_names = [asin + "_" + os.path.basename(name) for name in image_names]
            info = None
        else:
            return item

        product_folder = self._make_product_folder(prod_url)

        for img_name, new_name in zip(image_names, new_image_names):
            img_path = os.path.join(self.image_folder, img_name)
            new_path = os.path.join(product_folder, new_name)
            shutil.copy(img_path, new_path)

        if info is not None:
            info_file = os.path.join(product_folder, "info.json")
            with open(info_file, "w") as f:
                json.dump(info, f)

            self.scraped_urls_file.write(prod_url + "\n")

        return item

    def _make_product_folder(self, product_url):
        product_folder_name = hashlib.sha1(to_bytes(product_url)).hexdigest()
        product_folder = os.path.join(self.output_dir, product_folder_name)
        os.makedirs(product_folder, exist_ok=True)
        return product_folder

    def close_spider(self, spider):
        try:
            self.scraped_urls_file.close()
        except Exception:
            pass

        try:
            shutil.rmtree(self.image_folder)
        except Exception:
            pass
