from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

from bs4 import BeautifulSoup

from newscrawler.items import NewscrawlerItem


class ElmostradorSpider(CrawlSpider):
    name = 'elmostrador'
    allowed_domains = ['elmostrador.cl']
    start_urls = ['https://www.elmostrador.cl/']

    rules = (
        Rule(LinkExtractor(
            allow=[r'[a-z\d\-]+/(?:[a-z\d\-]+/)\d{4}/\d{2}/\d{2}/[a-zA-Z\d\-]+/$'],
            deny=[r'tv/.*', r'.*\.pdf$']),
            callback='parse_item', follow=True),
        Rule(LinkExtractor(
            allow=[r'[a-z\d\-]+/(?:[a-zA-Z\d\-]+/)?(?:page/\d+/)?$']), follow=True),
    )

    def parse_item(self, response):
        soup = BeautifulSoup(response.body)

        published_time = soup.find('meta', property='article:published_time').attrs['content'][:19]
        url = response.url
        author = soup.find('p', class_='autor-y-fecha').find('span').get_text()
        title = soup.find('section', class_='datos-noticias').find('h2').get_text(strip=True)
        description = soup.find('section', class_='noticia-single-post').find('figcaption').get_text(strip=True)
        content = soup.find('div', id='noticia')

        # Delete unwanted elements
        related_title = content.find('strong', text='También te puede interesar:')
        related_links = content.find_all('a', rel='noopener')
        gnews = content.find('div', class_='gnews-container')
        style = content.find('style')

        if related_title is not None:
            related_title.decompose()

        if related_links is not None:
            for link in related_links:
                link.decompose()

        if gnews is not None:
            gnews.decompose()

        if style is not None:
            style.decompose()

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
