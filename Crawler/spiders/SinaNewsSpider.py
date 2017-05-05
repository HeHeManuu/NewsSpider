from scrapy.spiders import CrawlSpider
from scrapy.spiders import Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.selector import Selector
from Crawler.items import NewsItem
from Crawler.util import *
import re
import Crawler.settings
import scrapy


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
            allow_url.append(".*?/%d-\d+/.*?" % x)
    return allow_url


class SinaNewsSpider(CrawlSpider):
    name = "sina_news"
    allowed_domains = [
                       "news.sina.com.cn",
                       "tech.sina.com.cn",
                       "finance.sina.com.cn"
                       ]

    start_urls = [
        'http://news.sina.com.cn',
        'http://sina.com.cn',
        'http://news.sina.com.cn/china/'
    ]
    deny_urls = [
        r'.*?news.sina.com.cn.*?/\d{4}-\d{2}-\d{2}/.*?',
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
        r'.*?.tags.*?'
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
        Rule(LinkExtractor(allow=get_sina_allow_url(), deny=deny_urls_news, deny_domains=deny_domains), callback="parse_item", follow=True)
    )

    @staticmethod
    def parse_item(response):
        sel = Selector(response)
        url = response.request.url
        if re.match(r'.*?sina.com.*?/\d{4}-\d{2}-\d{2}/.*?', url):
            content = response.xpath('//*[@id="artibody"]//p//text()').extract()
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
                    source=sel.xpath('//*[@data-sudaclick="media_name"]/text() | //*[@data-sudaclick="media_name"]/a/text()').extract_first(),
                    author=None
                )
                item = judge_time_news(item)
                if item:
                    yield item
