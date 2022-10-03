from datetime import datetime

from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

from newscrawler.items import NewscrawlerItem
from newscrawler.spiders.utils import *


class LacuartaSpider(CrawlSpider):
    name = 'lacuarta'
    allowed_domains = ['lacuarta.com']
    start_urls = ['http://lacuarta.com/']
    # 'archivo.lacuarta.com' 'https://archivo.lacuarta.com/'

    rules = (
        Rule(LinkExtractor(allow=r'[a-zA-Z\-]+/noticia/.+'), callback='parse_item', follow=True),
        # Rule(LinkExtractor(allow=r'.*'), follow=True),
    )

    def parse_item(self, response):
        date = response.xpath('//time/@datetime').get()
        locale = response.xpath('//html/@lang').get()

        category = []
        category.extend(response.xpath('//li[contains(@class, "lvi-story-tags")]/a/text()').getall())
        category.extend(response.css('section.story-title div.story-meta-sections a::text').getall())

        category = [c[:2:] if c.startswith('/ ') else c for c in category]

        title = response.css('section.story-title h1::text').get()
        description = response.css('div.story-subtitle>p::text').get()

        content = response.css('div.body>section p,div.body>section h2').getall()

        line_to_delete = '<h2 class="">Mira las fotos a continuación:</h2>'
        if line_to_delete in content:
            content.remove(line_to_delete)

        author = response.css('div.story-author a::text').get() or response.css('div.story-author span::text').get()

        item = NewscrawlerItem()
        item['author'] = author
        item['published_time'] = datetime.strptime(date, "%Y-%m-%dT%H:%M:%S%z")
        item['locale'] = locale
        item['url'] = response.xpath('//meta[@property="og:url"]/@content').get()
        item['category'] = list(map(str.strip, category))
        item['title'] = title
        item['description'] = description
        item['content'] = ''.join(content)
        return item
