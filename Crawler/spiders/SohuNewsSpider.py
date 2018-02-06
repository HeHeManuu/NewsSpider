from scrapy.spiders import CrawlSpider
from scrapy.spiders import Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.selector import Selector
from Crawler.items import NewsItem
from Crawler.utils import *
import re
import Crawler.settings
import scrapy


def get_sohu_allow_url():
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


class SohuNewsSpider(CrawlSpider):
    name = "sohu_news"
    allowed_domains = [
        "www.sohu.com",
        "news.sohu.com",
        "business.sohu.com",
        "sports.sohu.com",
        "learning.sohu.com",
        "it.sohu.com"
    ]

    start_urls = [
        'http://www.sohu.com',
        # 'http://news.sohu.com',
        # 'http://business.sohu.com',
        # 'http://news.sohu.com/scroll/',
        # "http://sports.sohu.com",
        # "http://learning.sohu.com",
        # "http://it.sohu.com"
    ]
    deny_urls = [
        r'.*?sohu.com/a/.*?',
        r'.*?.pinglun.*?',
        r'.*?.wurenji_b.*?',
        r'.*?.shuzi.*?',
        r'.*?picture.*?'

    ]
    deny_urls_news = [
        r'.*?.pinglun.*?',
        r'.*?.wurenji_b.*?',
        r'.*?.shuzi.*?',
        r'.*?picture.*?'
    ]
    deny_domains = [
        'tv.sohu.com',
        'auto.sohu.com',
        'soyule.sohu.com',
        'game.sohu.com'
    ]

    rules = (
        Rule(LinkExtractor(allow=".*?sohu.com.*?", deny=deny_urls),
             follow=True),
        Rule(LinkExtractor(allow=".*?sohu.com/a/.*?", deny=deny_urls_news,deny_domains=deny_domains),
             callback="parse_item", follow=True)
    )

    @staticmethod
    def parse_item(response):
        sel = Selector(response)
        url = response.request.url
        if re.match(r'.*?sohu.com.*?/\d+/.*?', url):
            content = response.xpath('//*[@itemprop="articleBody"]//p//text()').extract()
            # 有的段落并不是在p标签下，所以
            if len(content) < 3:
                content = response.xpath(
                    '//*[@itemprop="articleBody"]//p//text() | //*[@id="contentText"]//div/text()').extract()

            publish_time = sel.re(r'\d{4}-\d{2}-\d{2} {0,1}\d{2}:\d{2}:\d{2}')[0]
            if content:
                item = NewsItem(
                    domainname='http://sohu.com',
                    chinesename='搜狐网',
                    url=sel.root.base,
                    title=sel.xpath('//*[@itemprop="headline"]/text()').extract_first(),
                    subtitle=sel.css('.sub::text').extract_first(),
                    language='中文',
                    encodingtype='utf-8',
                    corpustype='网络',
                    timeofpublish=publish_time,
                    content=''.join(content),
                    source=sel.xpath('//*[@id="media_span"]/span/text()').extract_first(),
                    author=sel.xpath('//*[@id="author_baidu"]/text()').extract_first()
                )
                item = judge_time_news(item)
                if item:
                    yield item
