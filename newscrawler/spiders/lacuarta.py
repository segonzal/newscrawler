from datetime import datetime

from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

from newscrawler.items import NewscrawlerItem
from newscrawler.spiders.utils import *


class LacuartaSpider(CrawlSpider):
    name = 'lacuarta'
    allowed_domains = ['lacuarta.com', 'archivo.lacuarta.com']
    start_urls = ['http://lacuarta.com/', 'https://archivo.lacuarta.com/']

    rules = (
        Rule(LinkExtractor(allow=r'[a-zA-Z\-]+/noticia/.+'), callback='parse_item', follow=True),
        Rule(LinkExtractor(allow=r'.*'), follow=True),
    )

    def parse_item(self, response):
        date = get_first_not_none(
            response,
            [
                '//meta[@property="article:published_time"]/@content',
                '//time/@datetime',
            ]
        ).get()
        locale = get_first_not_none(
            response,
            [
                '//meta[@property="og:locale"]/@content',
                '//html/@lang',
            ]
        ).get()
        category = get_all(
            response,
            [
                '//meta[@property="article:tag"]/@content',
                '//li[contains(@class, "lvi-story-tags")]/a/text()',
                '//meta[@property="article:section"]/@content',
                '//section[@class="story-title"]//span[contains(@class, "h6")]/a/text()',
            ]
        )
        title = get_first_not_none(
            response,
            [
                '//div[@class="titulo-nota"]//h1//text()',
                '//section[@class="story-title"]//h1//text()',
            ]
        ).get()
        description = get_first_not_none(
            response,
            [
                '//div[contains(@class, "bajada-art")]',
                '//div[@class="story-subtitle"]/p',
            ]
        )
        content = get_first_not_none(
            response,
            [
                '//div[contains(@class, "nota-interior-tx")]',
                '//div[contains(@class, "body")]/section',
            ]
        ).get()
        item = NewscrawlerItem()
        item['published_time'] = datetime.strptime(date, "%Y-%m-%dT%H:%M:%S%z")
        item['locale'] = locale
        item['url'] = response.xpath('//meta[@property="og:url"]/@content').get()
        item['category'] = list(map(str.strip, category))
        item['title'] = title
        item['description'] = get_formatted_text(description) if description else ''
        item['content'] = [content]
        return item
