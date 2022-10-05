from datetime import datetime

from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

from newscrawler.items import NewscrawlerItem
from newscrawler.spiders.utils import *


class ElmostradorSpider(CrawlSpider):
    name = 'elmostrador'
    allowed_domains = ['elmostrador.cl']
    start_urls = ['https://www.elmostrador.cl/']

    rules = (
        Rule(LinkExtractor(allow=r'.*/\d{4}/\d{2}/\d{2}/.*', deny=[r'.*\.pdf$',
                                                                   r'tv/.*',
                                                                   r'noticias/multimedia/.*',
                                                                   r'noticias/mundo/.*',
                                                                   ]),
             callback='parse_item', follow=True),
        # Rule(LinkExtractor(allow=r'.*'), follow=True),
    )

    def parse_item(self, response):
        date = response.xpath('//meta[@property="article:published_time"]/@content').get()
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
                '//meta[@property="article:section"]/@content',
            ]
        )
        description = response.xpath('//meta[@property="og:description"]/@content').getall()
        author = response.xpath('//p[contains(@class, "autor-y-fecha")]//a/text()').get()
        content = response.css('div#noticia>p,div#noticia>h3').getall()

        line_to_delete = "<p><strong>También te puede interesar:</strong></p>"
        if line_to_delete in content:
            content.remove(line_to_delete)

        content = [c.replace('<h3', '<h2').replace('</h3>', '</h2>') for c in content]

        if author in ['DW', 'Reuters', 'BBC News Mundo', 'EFE', 'El Mostrador/ EFE']:
            return

        item = NewscrawlerItem()
        item['author'] = author
        item['published_time'] = datetime.strptime(date, "%Y-%m-%dT%H:%M:%S%z")
        item['locale'] = locale
        item['url'] = response.xpath('//meta[@property="og:url"]/@content').get()
        item['category'] = list(map(str.strip, category))
        item['title'] = response.xpath('//meta[@property="og:title"]/@content').get()
        item['description'] = max(description, key=len)
        item['content'] = ''.join(content)
        return item
