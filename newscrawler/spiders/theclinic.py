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
        category = map(lambda x: x[1:] if x.startswith('#') else x, category)

        author = response.css('span.autor>a::text').get() or response.css('span.autor::text').get()

        if author == 'Por The Clinic':
            author = "The Clinic"

        content = response.css('div.the-content>p,div.the-content>h2').getall()

        line_to_delete = '<p class="has-text-align-center"><strong>¡Por fin un Newsletter gratuito y de ' \
                         'calidá!</strong></p> '
        if line_to_delete in content:
            content.remove(line_to_delete)

        item = NewscrawlerItem()
        item['author'] = author
        item['published_time'] = datetime.strptime(date, "%Y-%m-%dT%H:%M:%S%z")
        item['locale'] = response.xpath('//meta[@property="og:locale"]/@content').get()
        item['url'] = response.xpath('//meta[@property="og:url"]/@content').get()
        item['category'] = list(category)
        item['title'] = response.xpath('//meta[@property="og:title"]/@content').get()[:-13]
        item['description'] = response.css('p.bajada::text').get()
        item['content'] = content
        return item
