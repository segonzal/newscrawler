# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import uuid
from datetime import datetime

TRANSLATION_TABLE = str.maketrans('', '', '\xa0\xad')


class NewscrawlerPipeline:
    def process_item(self, item, spider):
        item['uid'] = str(uuid.uuid5(uuid.NAMESPACE_URL, item['url'])).replace('-', '')
        item['crawl_time'] = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S")
        item['site_name'] = spider.name
        item['content'] = item['content'].translate(TRANSLATION_TABLE).strip()
        return item
