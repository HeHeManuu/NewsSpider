from scrapy.spiders import CrawlSpider
from scrapy.spiders import Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.selector import Selector
from scrapy.http import Request
from Crawler.items import NewsItem
from Crawler.util import judge_time_news
from Crawler.settings import *
import re


def get_163_allow_url():
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
                allow_url.append('.*?/%s/%s/.*?' % (str(start_time.year)[2:], string))
        else:
            for x in range(start_time.month, NOW.month + 1):
                allow_url.append(
                    ".*?/%s/%s\d+.*?" % (str(start_time.year)[2:], (str(x) if x >= 10 else '0' + str(x))))
    else:
        for x in range(start_time.year, NOW.year + 1):
            allow_url.append(".*?/%s/\d+/.*?" % str(x)[2:])
    return allow_url


class NewsSpider(CrawlSpider):
    name = "wyxw_news"
    allowed_domains = ["news.163.com"]

    start_urls = [
                  'http://news.163.com',
                  'http://news.163.com/special/0001386F/rank_news.html'
                  ]
    deny_urls = [
        r'.*?news.163.com.*?/\d{2}/\d{4}/.*?',
        r'.*?.photo.*?',
        r'.*?.video.*?',
        r'.*?.picstory.*?'
    ]
    deny_domain = [
        'comment.news.163.com',
        'caozhi.news.163.com',
        'zajia.news.163.com',
        'v.news.163.com',
        'd.news.163.com'
    ]
    rules = (
        Rule(LinkExtractor(allow=".*?news.163.com.*?", deny=deny_urls, deny_domains=deny_domain), follow=True),
        Rule(LinkExtractor(allow=get_163_allow_url(), deny_domains=deny_domain), callback="parse_item", follow=True)
    )

    @staticmethod
    def parse_item(response):
        sel = Selector(response)
        url = response.request.url
        news_urls = sel.css('a::attr(href)').extract()
        if re.match(r'.*?news.163.com.*?/\d+/\d+/.*?', response.request.url):
            content = response.xpath('//*[@id="endText"]//p//text()').extract()
            need_removes = response.xpath('//*[@id="endText"]//p//style/text()').extract()
            # 移除原标题
            otitle = response.xpath('//p[@class="otitle"]/text()').extract_first()
            if otitle:
                content.remove(otitle)

            if need_removes:
                for i, need_remove in enumerate(content):
                    if need_remove.startswith('\n\t') or need_remove.count('=') > 6:  # 将可能出现的视频页面乱码去除
                        content[i] = ''
            title = sel.css('#epContentLeft > h1::text').extract_first()
            if not title:
                title = sel.css('head > title::text').extract_first()
                index = title.find('_')
                title = title[:index]
            if content:
                item = NewsItem(
                    domainname='http://news.163.com',
                    chinesename='网易新闻',
                    url=sel.root.base,
                    title=title,
                    language='中文',
                    encodingtype='utf-8',
                    corpustype='网络',
                    timeofpublish=sel.re(
                        r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}')[0],
                    content=''.join(content),
                    source=sel.css('#ne_article_source::text').extract_first(),
                    author=sel.css('div.author_txt > span.name::text').extract_first()
                )
                item = judge_time_news(item)
                if item:
                    yield item
