import time
import datetime
from Crawler.settings import *


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
        else:
            struct_time = datetime.datetime.strptime(news_time, "%Y-%m-%d %H:%M:%S")
        subtime = (NOW-struct_time).days
        if subtime < end_day:
            return item
        else:
            return None
    return None


def get_allow_url():
    """
    获得允许的url匹配,通过日期匹配
    :return: 
    """
    start_time = NOW - datetime.timedelta(END_DAY)
    allow_url = list()
    if start_time.year == NOW.year:
        if start_time.month == NOW.month:
            for x in range(start_time.day, NOW.day + 1):
                string = str(start_time.strftime('%m')) + (str(x) if x >= 10 else '0' + str(x))
                allow_url.append('.*?/%d/%s/.*?' % (start_time.year, string))
        else:
            for x in range(start_time.month, NOW.month + 1):
                allow_url.append(
                    ".*?/%d/%s\d+.*?" % (start_time.year, (str(x) if x >= 10 else '0' + str(x))))
    else:
        for x in range(start_time.year, NOW.year + 1):
            allow_url.append(".*?/%d/\d+/.*?" % x)
    return allow_url
