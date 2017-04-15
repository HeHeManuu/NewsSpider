# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import json
from Crawler.settings import *
import re
import os
import pymongo


class CrawlerPipeline(object):
    def __init__(self):
        self.file = open('items.jl', 'w', encoding='utf-8')
        self.url_seen = set()

    def process_item(self, item, spider):
        if item['url'] in self.url_seen:
            raise print("Duplicate item found: %s" % item)
        else:
            self.url_seen.add(item['url'])
            line = json.dumps(dict(item), ensure_ascii=False)+"\n"
            self.file.write(line)
            # 写入文档中
            path = 'Chinese\\'  # +item['domainname'].replace('http://', '')+'\\'
            time_str = item['timeofpublish']
            if '年' in time_str:
                time_str = datetime.datetime.strptime(time_str, "%Y年%m月%d日%H:%M").strftime('%Y-%m-%d')
            m = re.search(r'\d{4}-\d{2}-\d{2}', time_str)
            if m:
                time_str = m.group(0)
            time_path = time_str.replace('-', '\\')
            path = SAVE_PATH+path+time_path+'\\'
            if not os.path.exists(path):
                os.makedirs(path)
            url = item['url'].replace('http:/', '_').replace('/', '_').replace(':', '')
            filename = '0_'+spider.name+'_'+time_str+url+'.json'
            file1 = open(path+filename, 'w', encoding='utf-8')
            file1.write(line)
            file1.close()
        return item

    def close_spider(self, spider):
        self.file.close()


class MongoPipeline(object):

    collection_name = 'all_news'

    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DATABASE', 'items')
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        self.db[self.collection_name].insert(dict(item))
        return item