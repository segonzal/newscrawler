# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import uuid
from datetime import datetime

from itemadapter import ItemAdapter


class NewscrawlerPipeline:
    def process_item(self, item, spider):
        item['uid'] = str(uuid.uuid5(uuid.NAMESPACE_URL, item['url'])).replace('-', '')
        item['crawl_time'] = datetime.utcnow()
        return item
