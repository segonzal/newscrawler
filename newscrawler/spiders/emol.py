from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

from newscrawler.items import NewscrawlerItem

from bs4 import BeautifulSoup


class EmolSpider(CrawlSpider):
    name = 'emol'
    allowed_domains = ['emol.com']
    start_urls = ['https://www.emol.com/sitemap/']

    rules = (
        Rule(LinkExtractor(
            allow=[r'noticias/' + section + r'/\d{4}/\d{2}/\d{2}/\d+/[\da-zA-Z\-]+\.html' for section in [
                r'360',
                r'Autos',
                r'Cultura-y-Espectaculos',
                r'[Dd]eportes',
                r'[Ee]conomia',
                r'Espectaculos',
                r'[Ii]nternacional',
                r'magazine',
                r'Motores',
                r'[Nn]acional',
                r'[Tt]ecnologia',
                r'Tendencias',
                r'todas',
            ]],
            deny=[r'noticias/' + section + r'/\d{4}/\d{2}/\d{2}/\d+/[\da-zA-Z\-]+\.html' for section in [
            ]]), callback='parse_item', follow=False),
        Rule(LinkExtractor(
            allow=[
                r'sitemap/noticias/\d{4|/index.html',
                r'sitemap/noticias/\d{4}/emol_noticias.*\.html',
            ],
            deny=[
                r'sitemap/noticias/\d{4}/emol_videos.*\.html',
                r'sitemap/noticias/\d{4}/emol_fotos.*\.html',
            ]), follow=True)
    )

    def parse_item(self, response):
        soup = BeautifulSoup(response.body)

        # Server Error
        if soup.find('title').get_text() == "Object reference not set to an instance of an object.":
            return

        nota_info = soup.find('div', class_='info-notaemol-porfecha')

        if nota_info is None:
            return

        published_time = soup.find('meta', property='article:published_time').attrs['content']
        url = response.url
        author = nota_info.get_text().split('|')[-1].strip()
        title = soup.find('h1', id='cuDetalle_cuTitular_tituloNoticia').get_text()
        description = soup.find('h2', id='cuDetalle_cuTitular_bajadaNoticia').get_text()
        content = [c.get_text(' ', strip=True) for c in soup.find('div', id='cuDetalle_cuTexto_textoNoticia').children]
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
