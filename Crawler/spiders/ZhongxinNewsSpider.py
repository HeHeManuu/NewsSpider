from scrapy.spiders import CrawlSpider
from scrapy.spiders import Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.selector import Selector
from Crawler.items import NewsItem
from Crawler.utils import *
import re
import Crawler.settings
import scrapy


def get_zhong_allow_url():
    """
    获得允许的url匹配,通过日期匹配
    :return: 
    """
    start_time = NOW - datetime.timedelta(END_DAY)
    allow_url = list()
    if END_DAY < 21:
        return get_allow_date('%Y/%m-%d')
    if start_time.year == NOW.year:
        if start_time.month == NOW.month:
            for x in range(start_time.day, NOW.day + 1):
                string = str(start_time.strftime('%m')) + "-" + (str(x) if x >= 10 else '0' + str(x))
                allow_url.append('.*?/%d/%s/.*?' % (start_time.year, string))
        else:
            for x in range(start_time.month, NOW.month + 1):
                allow_url.append(
                    ".*?/%d/%s-\d+.*?" % (start_time.year, (str(x) if x >= 10 else '0' + str(x))))
    else:
        for x in range(start_time.year, NOW.year + 1):
            allow_url.append(".*?/%d/\d+.*?" % x)
    return allow_url


class ZhongxinNewsSpider(CrawlSpider):
    name = "zhongxin_news"
    allowed_domains = [
        "www.chinanews.com",
        "sports.chinanews.com",
        "finance.chinanews.com"
    ]

    start_urls = [
        'http://www.chinanews.com/importnews.html',
        'http://www.chinanews.com', "http://www.chinanews.com/scroll-news/news1.html",
        "http://finance.chinanews.com/"
    ]
    deny_urls = [
        r'.*?chinanews.com.*?/\d{4}/\d{2}-\d{2}/.*?',
        r'.*?.shipin.*?',
        r'.*?.piaowu.*?',
        r'.*?.kong.*?'
    ]
    deny_urls_news = [
        r'.*?.shipin.*?',
        r'.*?.piaowu.*?',
        r'.*?.kong.*?',
        r'.*?chinanews.com/tp.*?'
    ]
    deny_domains = [
        'photo.chinanews.com',
        'life.chinanews.com',
        'wine.chinanews.com'

    ]

    rules = (
        Rule(LinkExtractor(allow=".*?chinanews.com*?", deny=deny_urls, deny_domains=deny_domains), follow=True),
        Rule(LinkExtractor(allow=get_zhong_allow_url(), deny=deny_urls_news, deny_domains=deny_domains),
             callback="parse_item", follow=True)
    )

    @staticmethod
    def parse_item(response):
        sel = Selector(response)
        url = response.request.url
        if re.match(r'.*?chinanews.com.*?/\d{4}/\d{2}-\d{2}/.*?', url):
            content = response.xpath('//*[@class="left_zw"]//p//text()').extract()

            publish_time = sel.re(r'\d{4}年\d{2}月\d{2}日 {0,1}\d{2}:\d{2}')[0]
            # 取出来源
            source = sel.xpath('//*[@class="left-t"]//text()').extract()
            source = ''.join(source)
            if '：' in source:
                source = source[source.rfind('：') + 1:source.find(" 参与")]
            else:
                source = None

            if ' ' in publish_time:
                publish_time = publish_time.replace(' ', '')
            if content:
                item = NewsItem(
                    domainname='http://chinanews.com',
                    chinesename='中新网',
                    url=sel.root.base,
                    title=sel.xpath('//*[@id="cont_1_1_2"]/h1/text()').extract_first(),
                    subtitle=sel.css('.sub::text').extract_first(),
                    language='中文',
                    encodingtype='utf-8',
                    corpustype='网络',
                    timeofpublish=publish_time,
                    content=''.join(content),
                    source=source,
                    author=sel.xpath('//*[@id="author"]/text()').extract_first()
                )
                item = judge_time_news(item)
                if item:
                    yield item
