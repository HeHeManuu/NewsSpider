from scrapy.spiders import CrawlSpider
from scrapy.spiders import Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.selector import Selector
from Crawler.items import NewsItem, CommentItem
from Crawler.util import *
import re
import Crawler.settings
import scrapy
import requests
import json


def get_people_allow_url():
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


class QQNewsSpider(CrawlSpider):
    name = "qq_news"
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
        "news.qq.com",
        "finance.qq.com",
        "edu.qq.com",
        'mil.qq.com',
        'tech.qq.com',
        'sports.qq.com',
        'http://qq.com'
    ]
    deny_domains = [
        "view.news.qq.com"
    ]

    rules = (
        Rule(LinkExtractor(allow=".*?qq.com.*?", deny=r'.*?qq.com/a/\d{8}/.*?', deny_domains=deny_domains),
             follow=True),
        Rule(LinkExtractor(allow=get_people_allow_url(), deny_domains=deny_domains), callback="parse_item", follow=True)
    )

    @staticmethod
    def parse_item(response):
        sel = Selector(response)
        url = response.request.url
        if re.match(r'.*?qq.com/a/\d+/.*?', url) and '#p' not in url:
            content = response.xpath(
                '//*[@id="Cnt-Main-Article-QQ"]/p/text() | //*[@id="Cnt-Main-Article-QQ"]/p/strong/text()').extract()
            if content:
                item = NewsItem(
                    domainname='http://qq.com',
                    chinesename='腾讯网',
                    url=sel.root.base,
                    title=sel.css(
                        '#Main-Article-QQ > div > div.qq_main > div.qq_article > div.hd > h1::text').extract_first(),
                    subtitle=sel.css('.sub::text').extract_first(),
                    language='中文',
                    encodingtype='utf-8',
                    corpustype='网络',
                    timeofpublish=sel.re(
                        r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}')[0],
                    content=''.join(content),
                    source=sel.css(
                        '#Main-Article-QQ > div > div.qq_main > div.qq_article > div.hd > div > div.a_Info > span.a_source::text,#Main-Article-QQ > div > div.qq_main > div.qq_article > div.hd > div > div.a_Info > span.a_source > a::text').extract_first(),
                    author=sel.css('p.author::text').extract_first()
                )
                item = judge_time_news(item)
                if item:
                    news_id = re.search("cmt_id = ([\\d]*?);", response.text)
                    if news_id:
                        news_id = news_id.group(1)
                    comment = QQNewsSpider.get_comments(url, news_id)
                    yield item
                    if comment:
                        yield comment

    @staticmethod
    def get_comments(news_url, news_id):
        s1 = 'http://coral.qq.com/article/'
        s2 = '/comment?commentid='
        s3 = '&reqnum='
        s = s1 + news_id + s2

        offset, limit = 0, 100000
        url = s + str(offset) + s3 + str(limit)
        # res = requests.get(url=url, params={'headers': {
        #     'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'},
        #     'Connection': 'keep-alive',
        #     'Cache-Control': 'max-age=0',
        #     'Upgrade-Insecure-Requests': 1,
        #     'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        #     'Accept-Encoding': 'gzip, deflate',
        #     'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.6'}).text
        sess = requests.Session()
        sess.headers.update({'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'})
        res = sess.get(url)
        t = type(res.text)
        res = res.text.encode('latin-1').decode('utf8','surrogateescape')

        comment_item = CommentItem(
            url=news_url,
            comments=res
        )
        return comment_item
