# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import uuid
from datetime import datetime

from itemadapter import ItemAdapter
from markdownify import markdownify

TRANSLATION_TABLE = str.maketrans('', '', '\xa0\xad')


class NewscrawlerPipeline:
    def process_item(self, item, spider):
        item['uid'] = str(uuid.uuid5(uuid.NAMESPACE_URL, item['url'])).replace('-', '')
        item['crawl_time'] = datetime.utcnow()
        item['site_name'] = spider.name

        category = item['category']
        category = map(str.strip, category)
        category = map(str.lower, category)
        item['category'] = list(category)

        for key in ['title', 'description', 'content']:
            item[key] = item[key].translate(TRANSLATION_TABLE).strip()
        return item
