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
        Rule(LinkExtractor(allow=r'.+/noticia/.*', deny=[r'la-tercera-tv/noticia/.*',
                                                         r'mundo/noticia/.*']),
             callback='parse_item', follow=True),
        # Rule(LinkExtractor(allow=r'.*'), follow=True),
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

        content = response.css('article div.single-content')
        content = content.css('p.paragraph, div.header').getall()
        # , div.header

        if '</div></h2></div>' in content[-1]:
            content = content[:-2]

        author = ' '.join(response.css('div.author div.name *::text').getall())
        if author in ['Agencia Bloomberg', 'EFE', 'Europa Press']:
            return

        item = NewscrawlerItem()
        item['author'] = author
        item['published_time'] = datetime.strptime(date[:19], "%Y-%m-%dT%H:%M:%S")
        item['locale'] = locale
        item['url'] = response.xpath('//meta[@property="og:url"]/@content').get()
        item['category'] = list(map(str.strip, category))
        item['title'] = response.xpath('//meta[@property="og:title"]/@content').get()[:-13]
        item['description'] = max(description, key=len)
        item['content'] = content
        return item
