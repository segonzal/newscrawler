from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

from newscrawler.items import NewscrawlerItem

from bs4 import BeautifulSoup


class TheclinicSpider(CrawlSpider):
    name = 'theclinic'
    allowed_domains = ['theclinic.cl']
    start_urls = ['http://theclinic.cl/']

    rules = (
        Rule(LinkExtractor(
            allow=[r'\d{4}/\d{2}/\d{2}/[a-z\d\-]+/']),
            callback='parse_item', follow=True),
        Rule(LinkExtractor(
            allow=[r'etiqueta/[a-z]+/(?:page/\d+/)?',
                   r'noticias/[a-z]+/[a-z]+/(?:page/\d+/)?']),
            follow=True),
    )

    def parse_item(self, response):
        soup = BeautifulSoup(response.body)

        article = soup.find('article', class_='principal')

        published_time = soup.find('meta', property='article:published_time').attrs['content'][:19]
        url = response.url
        author = article.find('span', class_='autor').get_text(strip=True)
        title = article.find('h1').get_text(strip=True)
        description = article.find('p', class_='bajada')
        description = '' if description is None else description.get_text(strip=True)
        content = article.find('div', class_='the-content')

        # remove script
        # bloque-dfp bloque-tc-un-recomendado bloque-tc-cita-destacada bloque-mgid bloque-tc-dos-recomendados
        for tag in [*content.find_all('script'),
                    *content.find_all(class_='bloque-dfp'),
                    *content.find_all(class_='bloque-tc-un-recomendado'),
                    *content.find_all(class_='bloque-tc-cita-destacada'),
                    *content.find_all(class_='bloque-mgid'),
                    *content.find_all(class_='bloque-tc-dos-recomendados')]:
            tag.decompose()

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
