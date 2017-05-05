from scrapy.spiders import CrawlSpider
from scrapy.spiders import Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.selector import Selector
from Crawler.items import NewsItem
from Crawler.util import *
import re
import Crawler.settings
import scrapy


def get_xin_allow_url():
    """
    获得允许的url匹配,通过日期匹配
    :return: 
    """
    start_time = NOW - datetime.timedelta(END_DAY)
    allow_url = list()
    if start_time.year == NOW.year:
        if start_time.month == NOW.month:
            for x in range(start_time.day, NOW.day + 1):
                string = str(start_time.strftime('%m')) + '/' + (str(x) if x >= 10 else '0' + str(x))
                allow_url.append('.*?/%d-%s/.*?' % (start_time.year, string))
        else:
            for x in range(start_time.month, NOW.month + 1):
                allow_url.append(
                    ".*?/%d-%s/\d+.*?" % (start_time.year, (str(x) if x >= 10 else '0' + str(x))))
    else:
        for x in range(start_time.year, NOW.year + 1):
            allow_url.append(".*?/%d-\d+/.*?" % x)
    return allow_url


class XinHuaNewsSpider(CrawlSpider):
    name = "xinhua_news"
    allowed_domains = [
                       "news.xinhuanet.com",
                       "news.cn"
                       ]

    start_urls = [
        'http://news.xinhuanet.com',
        'http://news.cn',
        'http://xinhuanet.com'
    ]
    deny_urls = [
        r'.*?news.xinhuanet.com.*?/\d{4}-\d{2}/\d{2}/.*?',
        r'.*?.photo.*?',
        r'.*?.video.*?',
        r'.*?.comments.*?',
        r'.*?.auto.*?',
        r'.*?.forum.*?',
        r'.*?.caipiao.*?'
    ]
    deny_urls_news = [
        r'.*?.photo.*?',
        r'.*?.video.*?',
        r'.*?.comments.*?',
        r'.*?.auto.*?',
        r'.*?.forum.*?',
        r'.*?.caipiao.*?'
    ]

    rules = (
        Rule(LinkExtractor(allow=".*?xinhuanet.com.*?", deny=deny_urls), follow=True),
        Rule(LinkExtractor(allow=get_xin_allow_url(), deny=deny_urls_news), callback="parse_item", follow=True)
    )

    @staticmethod
    def parse_item(response):
        sel = Selector(response)
        url = response.request.url
        if re.match(r'.*?xinhuanet.com.*?/\d{4}-\d{2}/\d{2}/.*?', url) :
            content = response.xpath('//*[@id="p-detail"]//p//text()').extract()
            if content:
                item = NewsItem(
                    domainname='http://xinhuanet.com',
                    chinesename='新华网',
                    url=sel.root.base,
                    title=sel.css('div > div.h-title::text').extract_first(),
                    subtitle=sel.css('.sub::text').extract_first(),
                    language='中文',
                    encodingtype='utf-8',
                    corpustype='网络',
                    timeofpublish=sel.re(
                        r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}')[0],
                    content=''.join(content),
                    source=sel.css('#source::text').extract_first(),
                    author=None
                )
                item = judge_time_news(item)
                if item:
                    yield item
