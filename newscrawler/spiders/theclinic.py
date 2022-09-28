import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule

from datetime import datetime
from newscrawler.items import NewscrawlerItem
from newscrawler.spiders.utils import *


class TheclinicSpider(CrawlSpider):
    name = 'theclinic'
    allowed_domains = ['theclinic.cl']
    start_urls = ['http://theclinic.cl/']

    # https://www.theclinic.cl/2022/09/20/boric-nueva-york-espana-allende-onu/
    rules = (
        Rule(LinkExtractor(allow=r'\d{4}/\d{2}/\d{2}/.*'), callback='parse_item', follow=True),
    )

    def parse_item(self, response):
        # <meta property="article:published_time" content="2022-09-20T09:00:00+00:00">
        date = response.xpath('//meta[@property="article:published_time"]/@content').get()
        if date is None:
            return
        date = list(date)
        date.pop(-3)
        date = ''.join(date)

        category = get_all(
            response,
            [
                '//a[@class="tag"]/@title',
                '//h2[@class="seccion"]/a/@title',
            ]
        )
        category = map(str.strip, category)
        category = map(lambda x: x[1:] if x.startswith('#') else x, category)

        item = NewscrawlerItem()
        item['published_time'] = datetime.strptime(date, "%Y-%m-%dT%H:%M:%S%z")
        item['locale'] = response.xpath('//meta[@property="og:locale"]/@content').get()
        item['url'] = response.xpath('//meta[@property="og:url"]/@content').get()
        item['category'] = list(category)
        item['title'] = response.xpath('//meta[@property="og:title"]/@content').get()[:-13]
        item['description'] = response.css('p.bajada::text').get()
        item['content'] = [response.xpath('//div[@class="the-content"]').get()]
        return item
