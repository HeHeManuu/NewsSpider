from scrapy.spiders import CrawlSpider
from scrapy.spiders import Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.selector import Selector
from Crawler.items import NewsItem, CommentItem
from Crawler.utils import *
import re
import Crawler.settings
import scrapy
import requests
import json


def get_QQ_allow_url():
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
                allow_url.append('.*?/%d%s/.*?' % (start_time.year, string))
        else:
            for x in range(start_time.month, NOW.month + 1):
                allow_url.append(
                    ".*?/%d%s\d+.*?" % (start_time.year, (str(x) if x >= 10 else '0' + str(x))))
    else:
        for x in range(start_time.year, NOW.year + 1):
            allow_url.append(".*?/%d\d+/.*?" % x)
    return allow_url


class QQCommentSpider(CrawlSpider):
    name = "qq_comments"
    allowed_domains = ["news.qq.com",
                       "finance.qq.com",
                       "edu.qq.com",
                       'mil.qq.com',
                       'tech.qq.com',
                       'sports.qq.com',
                       'www.qq.com'
                       ]

    start_urls = [
        "http://news.qq.com/articleList/rolls/",
        "http://finance.qq.com/articleList/rolls/",
        "http://edu.qq.com/articleList/rolls/",
        'http://mil.qq.com/articleList/rolls/',
        'http://tech.qq.com/articleList/rolls/',
        'http://sports.qq.com/articleList/rolls/',
        "http://news.qq.com",
        "http://finance.qq.com",
        "http://edu.qq.com",
        'http://mil.qq.com',
        'http://tech.qq.com',
        'http://sports.qq.com',
        'http://www.qq.com'
    ]
    deny_domains = [
        "view.news.qq.com",
        'app.edu.qq.com'
    ]

    rules = (
        Rule(LinkExtractor(allow=".*?qq.com.*?", deny=r'.*?qq.com/a/\d{8}/.*?', deny_domains=deny_domains),
             follow=True),
        Rule(LinkExtractor(allow=get_QQ_allow_url(), deny_domains=deny_domains), callback="parse_item", follow=True)
    )

    @staticmethod
    def parse_item(response):
        url = response.request.url
        if re.match(r'.*?qq.com/a/\d+/.*?', url) and '#p' not in url:
            news_id = re.search("cmt_id = ([\\d]*?);", response.text)
            if news_id:
                news_id = news_id.group(1)
            comment = QQCommentSpider.get_comments(url, news_id)
            if comment:
                yield comment

    @staticmethod
    def get_comments(news_url, news_id):
        s1 = 'http://coral.qq.com/article/'
        s2 = '/comment?commentid='
        s3 = '&reqnum='
        s = s1 + news_id + s2

        all_comments = []

        offset, limit = 0, 100000
        url = s + str(offset) + s3 + str(limit)
        sess = requests.Session()
        sess.headers.update({'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'})
        res = sess.get(url)
        res = res.text.encode('latin-1').decode('utf8', 'surrogateescape')

        data = json.loads(res)
        for v in data['data']['commentid']:
            per_comment = dict()
            per_comment['against'] = 0
            per_comment['vote'] = v['up']
            per_comment['content'] = v['content']
            per_comment['location'] = v['userinfo']['region']
            per_comment['nick'] = v['userinfo']['nick']
            x = time.localtime(float(v['time']))  # localtime参数为float类型，这里1317091800.0为float类型
            t = time.strftime('%Y-%m-%d %H:%M:%S', x)
            per_comment['time'] = t
            all_comments.append(per_comment)

        if len(all_comments) == 0:
            return None
        comment_item = CommentItem(
            url=news_url,
            sitename='QQ',
            num_comments=len(all_comments),
            comments=all_comments
        )
        return comment_item
