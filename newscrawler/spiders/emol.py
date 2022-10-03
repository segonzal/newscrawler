from datetime import datetime

from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

from newscrawler.items import NewscrawlerItem
from newscrawler.spiders.utils import *

from bs4 import BeautifulSoup


class EmolSpider(CrawlSpider):
    name = 'emol'
    allowed_domains = ['emol.com']
    start_urls = ['https://www.emol.com/']

    rules = (
        Rule(LinkExtractor(allow=[r'noticias/Nacional/\d{4}/\d{2}/\d{2}/\d+/.*',
                                  r'noticias/Deportes/\d{4}/\d{2}/\d{2}/\d+/.*',
                                  r'noticias/Espectaculos/\d{4}/\d{2}/\d{2}/\d+/.*',
                                  ]), callback='parse_item', follow=True),
        # Rule(LinkExtractor(allow=r'.*'), follow=True),
    )

    def parse_item(self, response):
        date = response.xpath('//meta[@property="article:published_time"]/@content').get()
        locale = response.xpath('//meta[@property="og:locale"]/@content').get()
        category = get_all(
            response,
            [
                '//meta[@property="article:section"]/@content',
            ]
        )
        title = response.xpath('//meta[@property="og:title"]/@content').get()[:-11]
        description = response.xpath('//meta[@property="og:description"]/@content').get()

        author = response.css('div.info-notaemol-porfecha a::text').get() or \
                 response.css('div.info-notaemol-porfecha::text').get()
        author = author[author.rfind('|') + 1:].strip()

        if any([author.startswith(c) for c in ['AFP', 'La Nación', 'Aton']]):
            return

        content = response.css('div#cuDetalle_cuTexto_textoNoticia').get()
        content = BeautifulSoup(content)
        for s in content.find_all('script'):
            s.extract()
        for br in content.find_all('br'):
            br.replace_with('\n')
        content = content.get_text()

        item = NewscrawlerItem()
        item['author'] = author
        item['published_time'] = datetime.strptime(date, "%Y-%m-%dT%H:%M:%S")
        item['locale'] = locale
        item['url'] = response.xpath('//meta[@property="og:url"]/@content').get()
        item['category'] = list(map(str.strip, category))
        item['title'] = title
        item['description'] = description
        item['content'] = content
        return item
