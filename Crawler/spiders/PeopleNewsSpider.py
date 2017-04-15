from scrapy.spiders import CrawlSpider
from scrapy.contrib.spiders import Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.selector import Selector
from Crawler.items import NewsItem
from Crawler.util import *
import re
import Crawler.settings
import scrapy


class PeopleNewsSpider(CrawlSpider):
    name = "people_news"
    allowed_domains = ["politics.people.com.cn",
                       "world.people.com.cn",
                       "finance.people.com.cn",
                       "military.people.com.cn",
                       "opinion.people.com.cn",
                       "legal.people.com.cn",
                       "society.people.com.cn",
                       "edu.people.com.cn",
                       "house.people.com.cn",
                       "www.people.com.cn"
                       ]

    start_urls = [
        'http://people.com.cn'
    ]

    rules = (
        Rule(LinkExtractor(allow=".*?people.com.cn.*?", deny=r'.*?people.com.cn.*?/\d{4}/\d{4}/.*?'), follow=True),
        Rule(LinkExtractor(allow=get_allow_url()), callback="parse_item", follow=True)
    )
    # tuple(rule_list)

    @staticmethod
    def parse_item(response):
        sel = Selector(response)
        url = response.request.url
        if re.match(r'.*?people.com.cn.*?/\d+/\d+/.*?', url) and 'BIG' not in url:
            content = response.xpath('//*[@id="rwb_zw"]/p/text() | //*[@id="rwb_zw"]/p/strong/text()').extract()
            if content:
                item = NewsItem(
                    domainname='http://people.com.cn',
                    chinesename='人民网',
                    url=sel.root.base,
                    title=sel.css('div.text_title > h1::text').extract_first(),
                    subtitle=sel.css('.sub::text').extract_first(),
                    language='中文',
                    encodingtype='utf-8',
                    corpustype='网络',
                    timeofpublish=sel.re(
                        r'\d{4}年\d{2}月\d{2}日\d{2}:\d{2}')[0],
                    content=''.join(content),
                    source=sel.css('div.box01 > div.fl > a::text').extract_first(),
                    author=sel.css('p.author::text').extract_first()
                )
                item = judge_time_news(item)
                if item:
                    yield item
