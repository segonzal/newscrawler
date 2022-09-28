from datetime import datetime

from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

from newscrawler.items import NewscrawlerItem
from newscrawler.spiders.utils import *


class EmolSpider(CrawlSpider):
    name = 'emol'
    allowed_domains = ['emol.com']
    start_urls = ['https://www.emol.com/']

    rules = (
        Rule(LinkExtractor(allow=r'noticias/.+/\d{4}/\d{2}/\d{2}/\d+/.*'), callback='parse_item', follow=True),
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
        title = response.xpath('//meta[@property="og:title"]/@content').get()[:-11]
        description = response.xpath('//meta[@property="og:description"]/@content').get()
        item = NewscrawlerItem()
        item['published_time'] = datetime.strptime(date, "%Y-%m-%dT%H:%M:%S")
        item['locale'] = locale
        item['url'] = response.xpath('//meta[@property="og:url"]/@content').get()
        item['category'] = list(map(str.strip, category))
        item['title'] = title
        item['description'] = description
        item['content'] = [response.css('div#cuDetalle_cuTexto_textoNoticia div').get()]
        return item
