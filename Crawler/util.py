import time
import datetime
from Crawler.settings import *
from redis import Redis


def judge_time_news(item, end_day=END_DAY):
    """
    判断爬取的新闻是否符合时间约束
    :param item:
    :param end_day:
    :return: item or None
    """
    news_time = item.get("timeofpublish", None)
    if news_time:
        if '年' in news_time:
            struct_time = datetime.datetime.strptime(news_time, "%Y年%m月%d日%H:%M")
        elif news_time.count(':') == 1:
            struct_time = datetime.datetime.strptime(news_time, "%Y-%m-%d %H:%M")
        else:
            struct_time = datetime.datetime.strptime(news_time, "%Y-%m-%d %H:%M:%S")
        subtime = (NOW - struct_time).days
        if subtime < end_day:
            return item
        else:
            return None
    return None


class RedisFactory(object):
    def __init__(self, name):
        self.Redis = Redis(host='localhost', port=6379, db=0)
        self.name = name

    def insert(self, element):
        self.Redis.sadd(self.name, element)
        print(self.Redis.scard(self.name))

    def isExit(self, element):
        return self.Redis.sismember(self.name, element)

    def show(self):
        self.Redis.smembers(self.name)

    def flush(self):
        self.Redis.flushall()


if __name__ == "__main__":
    fa = RedisFactory("url")
    print(fa.Redis.scard(fa.name))
    # fa.flush()
    print(fa.Redis.scard(fa.name))