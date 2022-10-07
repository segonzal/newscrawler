from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

from newscrawler.items import NewscrawlerItem

from bs4 import BeautifulSoup


class LacuartaSpider(CrawlSpider):
    name = 'lacuarta'
    allowed_domains = ['lacuarta.com']
    start_urls = ['http://lacuarta.com/']

    rules = (
        Rule(LinkExtractor(
            allow=[r'[a-z\d\-]+/[a-z\d\-]+/[a-z\d\-]+/[A-Z\d]+/'],
            deny_domains=['comerciante.lacuarta.com',
                          'constructor.lacuarta.com']),
            callback='parse_item', follow=True),
        Rule(LinkExtractor(
            allow=[r'etiqueta/[a-z\d\-]*',
                   r'categoria/noticias/[a-z\d\-]*',
                   r'categoria/eventos/[a-z\d\-]*']),
            follow=True),
    )

    def parse_item(self, response):
        soup = BeautifulSoup(response.body)

        published_time = soup.find('time').attrs['datetime'][:19]
        url = response.url
        author = soup.find('div', class_='story-author').get_text(strip=True)
        title = soup.find('div', class_='story-headline').find('h1').get_text(strip=True)
        description = soup.find('div', class_='story-subtitle').find('p').get_text(strip=True)
        content = soup.find('div', class_='body').find('section')

        # Delete unwanted elements
        embedded = content.find_all('div', class_='story-embeded')

        if embedded is not None:
            for e in embedded:
                e.decompose()

        content = [c.get_text(' ', strip=True) for c in content.children]
        content = [c for c in content if len(c) != 0]
        content = '\n'.join(content)

        item = NewscrawlerItem()
        item['published_time'] = published_time
        item['url'] = url
        item['author'] = author
        item['title'] = title
        item['description'] = description
        item['content'] = content
        return item
