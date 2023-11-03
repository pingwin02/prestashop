import scrapy
import json
import os


class CategoriesSpider(scrapy.Spider):

    custom_settings = {
        'LOG_LEVEL': 'ERROR',
    }

    name = 'categories'
    start_urls = ['https://www.komputronik.pl']

    def parse(self, response):
        categories = {}
        all_links = []

        main_menu = response.css('ul.menu-tree-new')
        for main_category in main_menu.xpath('./li'):
            if main_category.css('a::text').get() == 'Usługi':
                continue
            categories[main_category.css('a::text').get()] = {}
            for sub_category in main_category.xpath('./ul/li'):

                sub_sub_categories = []
                sub_sub_categories_links = [sub_sub_category.css('a::attr(href)').get(
                ) for sub_sub_category in sub_category.xpath('./ul/li')][:10]
                for sub_sub_category in sub_sub_categories_links:
                    if 'category' in sub_sub_category:
                        link = f"https://www.komputronik.pl{sub_sub_category}"
                        if link not in all_links:
                            sub_sub_categories.append(link)
                            all_links.append(link)

                if len(sub_sub_categories) == 0:
                    continue

                categories[main_category.css('a::text').get()].update({
                    sub_category.css('a::text').get(): sub_sub_categories
                })

        if not os.path.exists('../scraper_results'):
            os.makedirs('../scraper_results')

        with open('../scraper_results/categories.json', 'w') as f:
            json.dump(categories, f, indent=4, ensure_ascii=False)
