import scrapy
import json
import os
import shutil

from scraper.items import ScraperItem


class ProductsSpider(scrapy.Spider):

    custom_settings = {
        'LOG_LEVEL': 'ERROR',
        'FEEDS': {
            '../scraper_results/products.json': {
                'format': 'json',
                'encoding': 'utf8',
                'indent': 4,
                'overwrite': True,
            },
        },
        'IMAGES_STORE': '../scraper_results/images',
        'ITEM_PIPELINES': {
            'scraper.pipelines.ProductImagePipeline': 1,
        },
    }

    name = 'products'

    counter = 0

    def start_requests(self):
        if os.path.exists('../scraper_results/images'):
            shutil.rmtree('../scraper_results/images')

        with open('../scraper_results/categories.json', 'r') as f:
            categories = json.load(f)

        for main_category in categories:
            for sub_category in categories[main_category]:
                for sub_sub_category in categories[main_category][sub_category]:
                    yield scrapy.Request(sub_sub_category, callback=self.parse, meta={'category': sub_category})

    def parse(self, response):
        for product in response.css("div.tests-product-entry")[:5]:
            product_link = product.css(
                "h2.font-headline").css("a::attr(href)").get()
            yield scrapy.Request(product_link, callback=self.parse_product, meta={'category': response.meta['category']})

    def parse_product(self, response):
        print(f"Scraping product #{self.counter}", end='\r')
        product = ScraperItem()

        product['id'] = response.url.split('/')[4]

        product['title'] = response.css(
            "h1.tests-product-name::text").get().strip()

        product['price'] = response.css(
            "div.leading-8::text").get()
        if product['price'].strip() == "":
            product['price'] = response.css(
                "div.leading-8 > span::text").get()
        product['price'] = product['price'].replace(
            "\xa0", '').replace(" zł", '').replace(",", ".").strip()

        product['category'] = response.meta['category']

        product['description'] = response.css(
            "div.cc-mobile-1 > p::text").get()
        if product['description'] is None or product['description'].strip() == "":
            product['description'] = response.css(
                "#p-content-product-desc > div > div > div:nth-child(2) > p").get()
        if product['description'] is None or product['description'].strip() == "":
            product['description'] = response.css(
                "#p-producer-desc > div > p").get()
        if product['description'] is not None:
            product['description'] = product['description'].replace("\n", " ").replace(
                "\xa0", " ").replace("\r", " ").replace("\t", " ").replace("<p>", "").replace("</p>", "").replace("<br>", "").replace("</br>", "").strip()
        if product['description'] is None or product['description'].strip() == "":
            product['description'] = "Brak opisu"

        product['attributes'] = {}
        for attribute in response.css("div.tests-full-specification > div > div:nth-child(2) > div.grid"):
            category = attribute.css(
                "div:nth-child(1) > span::text").get()
            if category is None or category.strip() == "":
                category = attribute.css(
                    "div:nth-child(1) > span > a::text").get()
            value = attribute.css("div:nth-child(2) > p::text").get()
            if value is None or value.strip() == "":
                value = attribute.css(
                    "div:nth-child(2) > p > a::text").get()
            product['attributes'][category.strip(
            )] = value.strip().replace("\n", " ")

        product['image_urls'] = []
        image_link = response.css(
            "ktr-gallery > div > div > section > div > ol > li > div > img::attr(src)").get()

        for i in range(2):
            link = image_link.replace(
                "/6/", "/11/").replace("1.jpg", f"{i+1}.jpg")
            product['image_urls'].append(link)

        self.counter += 1
        yield product

    def closed(self, reason):
        print(f"\nScraped {self.counter} products!")
