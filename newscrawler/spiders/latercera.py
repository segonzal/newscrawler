from datetime import datetime

from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

from newscrawler.items import NewscrawlerItem
from newscrawler.spiders.utils import *


class LaTerceraSpider(CrawlSpider):
    name = 'latercera'
    allowed_domains = ['latercera.com']
    start_urls = ['https://www.latercera.com/']

    rules = (
        Rule(LinkExtractor(allow=r'.+/noticia/.*'), callback='parse_item', follow=True),
        Rule(LinkExtractor(allow=r'.*'), follow=True),
    )

    def parse_item(self, response):
        date = response.xpath('//meta[@property="article:published_time"]/@content').get()
        locale = response.xpath('//meta[@property="og:locale"]/@content').get()
        category = get_all(
            response,
            [
                '//meta[@property="article:tag"]/@content',
                '//meta[@property="article:section"]/@content',
            ]
        )
        description = response.xpath('//meta[@property="og:description"]/@content').getall()
        item = NewscrawlerItem()
        item['published_time'] = datetime.strptime(date[:19], "%Y-%m-%dT%H:%M:%S")
        item['locale'] = locale
        item['url'] = response.xpath('//meta[@property="og:url"]/@content').get()
        item['category'] = list(map(str.strip, category))
        item['title'] = response.xpath('//meta[@property="og:title"]/@content').get()[:-13]
        item['description'] = max(description, key=len)
        item['content'] = [response.css('article div.single-content > p, div.header').get()]
        return item
