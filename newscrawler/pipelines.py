# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import uuid
from datetime import datetime

from itemadapter import ItemAdapter
from markdownify import markdownify


class NewscrawlerPipeline:
    def process_item(self, item, spider):
        item['uid'] = str(uuid.uuid5(uuid.NAMESPACE_URL, item['url'])).replace('-', '')
        item['crawl_time'] = datetime.utcnow()
        item['site_name'] = spider.name
        item['category'] = list(map(str.lower, item['category']))

        content = ''.join(item['content'])
        content = content.replace('\xa0', ' ')
        content = markdownify(content, strip=['a', 'img'])
        item['content'] = content.strip()
        return item
