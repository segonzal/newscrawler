import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from newscrawler.items import NewscrawlerItem


class LacuartaSpider(CrawlSpider):
    name = 'lacuarta'

    start_urls = ['http://lacuarta.com/']
    allowed_domains = ['lacuarta.com']

    rules = (
        Rule(LinkExtractor(allow=r'[a-zA-Z\-]+/noticia/.+'), callback='parse_item', follow=True),
        Rule(LinkExtractor(allow=r'.*'), follow=True),
    )

    field_extractor = [
        {
            'field': 'site_name',
            'xpath': [
                '//meta[@property="og:site_name"]/@content',
            ],
            'method': 'get',
        }, {
            'field': 'published_time',
            'xpath': [
                '//meta[@property="article:published_time"]/@content',
                '//time/@datetime',
            ],
            'method': 'get',
        }, {
            'field': 'locale',
            'xpath': [
                '//meta[@property="og:locale"]/@content',
                '//html/@lang',
            ],
            'method': 'get',
        }, {
            'field': 'url',
            'xpath': [
                '//meta[@property="og:url"]/@content',
            ],
            'method': 'get',
        }, {
            'field': 'section',
            'xpath': [
                '//meta[@property="article:section"]/@content',
                '//section[@class="story-title"]//span[contains(@class, "h6")]/a/text()',
            ],
            'method': 'get',
        }, {
            'field': 'tag',
            'xpath': [
                '//meta[@property="article:tag"]/@content',
                '//li[contains(@class, "lvi-story-tags")]/a/text()',
            ],
            'method': 'getall',
        }, {
            'field': 'title',
            'xpath': [
                '//div[@class="titulo-nota"]//h1//text()',
                '//section[@class="story-title"]//h1//text()',
            ],
            'method': 'get',
        }, {
            'field': 'description',
            'xpath': [
                '//div[contains(@class, "bajada-art")]//h2',
                '//div[@class="story-subtitle"]/p',
            ],
            'method': 'extracttext',
        }, {
            'field': 'content',
            'xpath': [
                '//div[contains(@class, "nota-interior-tx")]/*[self::p or self::h2]',
                '//div[contains(@class, "body")]/section/*[self::p or self::h2]',
            ],
            'method': 'extracttext',
        }]

    def parse_item(self, response):
        item = NewscrawlerItem()
        for s in self.field_extractor:
            selector = next(filter(None, map(lambda xp: response.xpath(xp), s['xpath'])), None)

            if not selector:
                return

            if s['method'] == 'extracttext':
                text = ''
                for tag in selector:
                    print(tag.root.tag)
                    #print(tag.xpath('//text()').getall())
            else:
                text = selector.__getattribute__(s['method'])()

            item[s['field']] = text

        # Tener el tipo del contenedor del texto, si es <p> unirlo con salto de linea, sino espacio.
        return item
