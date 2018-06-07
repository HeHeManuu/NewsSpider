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
from Crawler.utils import RedisFactory
from Crawler.items import TweetsItem, InformationItem, FollowsItem, FansItem
from Crawler.items import NewsItem, CommentItem, TibetNewsItem


class CrawlerPipeline(object):
    def __init__(self):
        # self.file = open('items.jl', 'w', encoding='utf-8')
        self.url_seen = set()
        self.redis = RedisFactory(REDIS_NAME)
        self.redis_tibet = RedisFactory(REDIS_NAME_TIBET)

    def process_item(self, item, spider):
        if isinstance(item, NewsItem):
            if item['url'] in self.url_seen:
                raise print("Duplicate item found: %s" % item)
            else:
                self.url_seen.add(item['url'])
                self.redis.insert(item['url'])
                line = json.dumps(dict(item), ensure_ascii=False) + "\n"
                # self.file.write(line)
                # 写入文档中
                path = 'Chinese\\'  # +item['domainname'].replace('http://', '')+'\\'
                time_str = item['timeofpublish']
                if '年' in time_str:
                    time_str = datetime.datetime.strptime(time_str, "%Y年%m月%d日%H:%M").strftime('%Y-%m-%d')
                m = re.search(r'\d{4}-\d{2}-\d{2}', time_str)
                if m:
                    time_str = m.group(0)
                item['date'] = time_str
                time_path = time_str.replace('-', '\\')
                path = SAVE_PATH + path + time_path + '\\'
                if not os.path.exists(path):
                    os.makedirs(path)
                url = item['url'].replace('http:/', '_').replace('/', '_').replace(':', '')
                filename = '0_' + spider.name + '_' + time_str + url + '.json'
                file1 = open(path + filename, 'w', encoding='utf-8')
                file1.write(line)
                file1.close()
        elif isinstance(item, TibetNewsItem):
            if item['url'] in self.url_seen:
                raise print("Duplicate item found: %s" % item)
            else:
                self.url_seen.add(item['url'])
                self.redis_tibet.insert(item['url'])
                line = json.dumps(dict(item), ensure_ascii=False) + "\n"
                # self.file.write(line)
                # 写入文档中
                path = 'Tibetan\\'  # +item['domainname'].replace('http://', '')+'\\'
                txt_path = 'txt\\' + path
                time_str = item['timeofpublish'][:10]
                if '年' in time_str:
                    time_str = datetime.datetime.strptime(item['timeofpublish'], "%Y年%m月%d日%H:%M").strftime('%Y-%m-%d')
                m = re.search(r'\d{4}-\d{2}-\d{2}', time_str)
                if m:
                    time_str = m.group(0)
                time_path = time_str.replace('-', '\\')
                path = TIBET_SAVE_PATH + path + time_path + '\\'
                if not os.path.exists(path):
                    os.makedirs(path)
                url = item['url'].replace('http:/', '_').replace('/', '_').replace(':', '')
                filename = '0_' + spider.name + '_' + time_str + url + '.json'
                file1 = open(path + filename, 'w', encoding='utf-8')
                file1.write(line)
                file1.close()

                txt_path = TIBET_SAVE_PATH + txt_path + time_path + '\\'
                if not os.path.exists(txt_path):
                    os.makedirs(txt_path)
                txt_filename = filename.replace('json', 'txt')
                content = item['title'] + '\n' + item['content']
                file2 = open(txt_path + txt_filename, 'w', encoding='utf-8')
                file2.write(content)
                file2.close()
        return item

    def close_spider(self, spider):
        pass


class MongoDBPipleline(object):
    def __init__(self):
        clinet = pymongo.MongoClient("localhost", 27017)
        db = clinet["Sina"]
        self.Information = db["Information"]
        self.Tweets = db["Tweets"]
        self.Follows = db["Follows"]

    def process_item(self, item, spider):
        """ 判断item的类型，并作相应的处理，再入数据库 """
        if isinstance(item, InformationItem):
            try:
                self.Information.insert(dict(item))
            except Exception:
                pass
        elif isinstance(item, TweetsItem):
            try:
                self.Tweets.insert(dict(item))
            except Exception:
                pass
        elif isinstance(item, FollowsItem):
            try:
                self.Follows.insert(dict(item))
            except Exception:
                pass
        return item


class MongoPipeline(object):

    db_name = 'all_news'
    db_comment = 'all_comments'

    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DATABASE')
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        if isinstance(item, NewsItem):
            key = {'url': item['url']}
            self.db[self.db_name].update(key, dict(item), upsert=True)
            return item
        elif isinstance(item, CommentItem):
            key = {'url': item['url']}
            self.db[self.db_comment].update(key, dict(item), upsert=True)
            return 'comments of ' + item['url']