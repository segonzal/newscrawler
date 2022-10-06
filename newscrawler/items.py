# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class NewscrawlerItem(scrapy.Item):
    uid = scrapy.Field()
    crawl_time = scrapy.Field()
    site_name = scrapy.Field()
    published_time = scrapy.Field()
    url = scrapy.Field()
    author = scrapy.Field()
    title = scrapy.Field()
    description = scrapy.Field()
    content = scrapy.Field()
