from typing import List
from scrapy.http import Response, TextResponse


def get_first_not_none(response: Response, xpath: List[str]):
    return next(filter(None, map(lambda xp: response.xpath(xp), xpath)), None)


def get_all(response: Response, xpath: List[str]):
    results = []
    for s in filter(None, map(response.xpath, xpath)):
        results.extend(s.getall())
    return results


def get_formatted_text(selector: TextResponse):
    text = ''
    for line in selector.xpath('.//*[self::p or self::h2]'):
        text += ''.join(line.xpath('.//text()').getall()) + '\n'
    text = text.replace(u'\xa0', u' ')
    return text.strip()
