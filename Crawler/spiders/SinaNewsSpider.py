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


class SinaNewsSpider(CrawlSpider):
    name = "sina_news"
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
        r'.*?.tags.*?'
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
        r'.*?.gaokao.*?'
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
            content = response.xpath('//*[@id="artibody"]//p//text() | //*[@id="article"]//p//text()').extract()
            # 移除编辑
            editor = response.xpath('//*[@class="article-editor"]/text()').extract_first()
            if editor:
                content.remove(editor)
            publish_time = sel.re(r'\d{4}年\d{2}月\d{2}日.{0,1}\d{2}:\d{2}')[0]
            if ' ' in publish_time:
                publish_time = publish_time.replace(' ', '')

            if content:
                item = NewsItem(
                    domainname='http://sina.com.cn',
                    chinesename='新浪网',
                    url=sel.root.base,
                    title=sel.css('#artibodyTitle::text, #main_title::text').extract_first(),
                    subtitle=sel.css('.sub::text').extract_first(),
                    language='中文',
                    encodingtype='utf-8',
                    corpustype='网络',
                    timeofpublish=publish_time,
                    content=''.join(content),
                    source=sel.xpath(
                        '//*[@data-sudaclick="media_name"]/text() | //*[@data-sudaclick="media_name"]/a/text() | //*[@id="top_bar"]/div/div[2]/span[2]/a/text()').extract_first(),
                    author=None
                )
                item = judge_time_news(item)
                if item:
                    num = response.xpath('//*[@class="more"]/em/text()').extract()
                    news_info = re.search("http://comment5.news.sina.com.cn/comment/skin/default.html\?(.*?)\"", response.text)
                    if news_info:
                        news_info = news_info.group(1)
                    comment = SinaNewsSpider.get_comments(url, news_info,int(num))
                    yield item
                    if comment:
                        yield comment

    @staticmethod
    def get_comments(news_url, news_info, num):
        s1 = 'http://comment5.news.sina.com.cn/page/info?version=1&format=json&'
        s2 = '&page='
        s3 = '&page_size='
        s = s1 + news_info + s2

        all_comments = dict()
        page, page_size = 0, 200
        i = 0
        while page * 200 < num:
            url = s + str(page) + s3 + str(page_size)
            sess = requests.Session()
            sess.headers.update({
                'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'})
            res = sess.get(url).text.encode("utf-8").decode('gb2312')
            all_comments[str(i)] = res
            i = i + 1
            page += 1

        comment_item = CommentItem(
            url=news_url,
            comments=res
        )
        return comment_item