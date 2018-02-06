from scrapy.spiders import CrawlSpider
from scrapy.spiders import Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.selector import Selector
from Crawler.items import NewsItem, CommentItem
from Crawler.utils import *
import re
import requests
import json


def get_sina_allow_url():
    """
    获得允许的url匹配,通过日期匹配
    :return: 
    """
    start_time = NOW - datetime.timedelta(END_DAY)
    allow_url = list()
    if start_time.year == NOW.year:
        if start_time.month == NOW.month:
            for x in range(start_time.day, NOW.day + 1):
                string = str(start_time.strftime('%m')) + '-' + (str(x) if x >= 10 else '0' + str(x))
                allow_url.append('.*?/%d-%s/.*?' % (start_time.year, string))
        else:
            for x in range(start_time.month, NOW.month + 1):
                allow_url.append(
                    ".*?/%d-%s-\d+.*?" % (start_time.year, (str(x) if x >= 10 else '0' + str(x))))
    else:
        for x in range(start_time.year, NOW.year + 1):
            allow_url.append(".*?/%d-\d+-\d+/.*?" % x)
    return allow_url


class SinaCommentSpider(CrawlSpider):
    name = "sina_comments"
    allowed_domains = [
        "www.sina.com.cn",
        "news.sina.com.cn",
        "tech.sina.com.cn",
        "finance.sina.com.cn",
        "sports.sina.com.cn",
        'edu.sina.com.cn',
        "mil.news.sina.com.cn"
    ]

    start_urls = [
        'http://news.sina.com.cn',
        'http://www.sina.com.cn',
        'http://news.sina.com.cn/china/',
        "http://tech.sina.com.cn",
        "http://finance.sina.com.cn",
        "http://sports.sina.com.cn",
        'http://edu.sina.com.cn',
        "http://mil.news.sina.com.cn"
    ]
    deny_urls = [
        r'.*?.sina.com.cn.*?/\d{4}-\d{2}-\d{2}/.*?',
        r'.*?.photo.*?',
        r'.*?.video.*?',
        r'.*?.comment.*?',
        r'.*?.slide.*?',
        r'.*?.vr.*?',
        r'.*?.hangpai.*?',
        r'.*?.live.*?',
        r'.*?.media.*?',
        r'.*?.tags.*?',
        r'.*?.ischool.*?',
        r'.*?.zhongkao.*?',
        r'.*?.cba.*?',
        r'.*?coverstory.*?',
        r'.*?fawen.*?',
        r'.*?sina.com.cn/z/.*?',
        r'.*?sina.com.cn/zl/.*?',
        r'.*?ask.*?'
    ]
    deny_urls_news = [
        r'.*?.photo.*?',
        r'.*?.video.*?',
        r'.*?.comment.*?',
        r'.*?.slide.*?',
        r'.*?.hangpai.*?',
        r'.*?.vr.*?',
        r'.*?.live.*?',
        r'.*?.media.*?',
        r'.*?.tags.*?',
        r'.*?.pc.*?',
        r'.*?.gaokao.*?',
        r'.*?csj.*?',
        r'.*?.ischool.*?',
        r'.*?.zhongkao.*?',
        r'.*?.cba.*?',
        r'.*?coverstory.*?',
        r'.*?fawen.*?',
        r'.*?sina.com.cn/z/.*?',
        r'.*?sina.com.cn/zl/.*?',
        r'.*?ask.*?'
    ]
    deny_domains = [
        'survey.news.sina.com.cn',
        'video.news.sina.com.cn',
        'photo.sina.com.cn',
        'slide.news.sina.com.cn',
        'zhongce.sina.com.cn'
    ]

    rules = (
        Rule(LinkExtractor(allow=".*?sina.com.cn*?", deny=deny_urls, deny_domains=deny_domains), follow=True),
        Rule(LinkExtractor(allow=get_sina_allow_url(), deny=deny_urls_news, deny_domains=deny_domains),
             callback="parse_item", follow=True)
    )

    @staticmethod
    def parse_item(response):
        sel = Selector(response)
        url = response.request.url
        if re.match(r'.*?sina.com.*?/\d{4}-\d{2}-\d{2}/.*?', url):
            news_id = re.search("comment_id:(.*?)\"", response.text)
            channel = re.search("comment_channel:(.*?);", response.text)
            if news_id:
                news_id = news_id.group(1)
            if channel:
                channel = channel.group(1)
            comment = SinaNewsSpider.get_comments(url, channel, news_id)
            if comment:
                yield comment



    @staticmethod
    def get_comments(news_url, channel, news_id):
        s1 = 'http://comment5.news.sina.com.cn/page/info?version=1&format=json&channel='
        s11 = '&newsid='
        s2 = '&page='
        s3 = '&page_size='
        s = s1 + channel + s11 + news_id + s2

        all_comments = []
        page, page_size = 1, 200
        num = 200
        while (page - 1) * 200 < num:
            url = s + str(page) + s3 + str(page_size)
            sess = requests.Session()
            sess.headers.update({
                'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'})
            res = sess.get(url).text.encode("utf-8").decode('gb2312')
            data = json.loads(res)
            if page == 1:
                num = data['result']['count']['show']
            if num == 0:
                break
            for v in data['result']['cmntlist']:
                per_comment = dict()
                per_comment['against'] = 0
                per_comment['vote'] = v['agree']
                per_comment['content'] = v['content']
                per_comment['location'] = v['area']
                per_comment['time'] = v['time']
                per_comment['nick'] = v['nick']
                all_comments.append(per_comment)
            page += 1

        if len(all_comments) == 0:
            return None
        comment_item = CommentItem(
            url=news_url,
            sitename='Sina',
            num_comments=len(all_comments),
            comments=all_comments
        )
        return comment_item