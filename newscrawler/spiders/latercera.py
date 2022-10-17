from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

from newscrawler.items import NewscrawlerItem

from bs4 import BeautifulSoup


def apply_priority(priority):
    def process_request(request, response):
        return request.replace(priority=priority)

    return process_request


class LaTerceraSpider(CrawlSpider):
    name = 'latercera'
    allowed_domains = ['latercera.com']
    start_urls = ['https://www.latercera.com/']

    rules = (
        Rule(LinkExtractor(
            allow=[r'[a-z\d\-]+/noticia/[a-z\-\d]+/[A-Z\d]+'],
            deny=[r'la-tercera-tv/noticia/[a-z\-\d]+/[A-Z\d]+'],
            deny_domains=['glamorama.latercera.com',
                          'laboratorio.latercera.com']),
            process_request=apply_priority(10),
            callback='parse_item', follow=True),
        Rule(LinkExtractor(
            allow=[r'autor/[a-z\-\d]+/(?:/page/\d+)?',
                   r'etiqueta/[a-z\-\d]+(?:/page/\d+)?',
                   r'canal/[a-z\-\d]+']),
            process_request=apply_priority(5),
            follow=True),
    )

    def parse_item(self, response):
        soup = BeautifulSoup(response.body)

        header = soup.find('div', class_='titulares')

        published_time = soup.find('meta', property='article:published_time').attrs['content'][:19]
        url = response.url
        author = soup.find('div', class_='author').find('div', class_='name').get_text(strip=True)
        title = header.find('h1').get_text(strip=True)
        description = header.find('p', class_='excerpt')
        description = '' if description is None else description.get_text(strip=True)
        content = soup.find('div', class_='single-content')

        if content is None:
            return

        content = content.find_all(['p', 'div'], class_=['paragraph', 'header'])

        content = [c.get_text(' ', strip=True) for c in content]
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
