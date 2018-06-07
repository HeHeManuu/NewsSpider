# -*- coding: utf-8 -*-
import re

from scrapy.linkextractors import LinkExtractor
from scrapy.selector import Selector
from scrapy.spiders import CrawlSpider
from scrapy.spiders import Rule
from Crawler.utils import *
from Crawler.items import TibetNewsItem


class TibetPeopleSpider(CrawlSpider):
    name = 'tibet_people'
    allowed_domains = [
        'tibet.people.com.cn'
    ]
    start_urls = [
        'http://tibet.people.com.cn'
    ]

    rules = (

        Rule(LinkExtractor(allow=r".*?tibet.people.com.cn/.*?", deny=r".*?tibet.people.com.cn/\d{8}.*?"),
             follow=True),
        Rule(LinkExtractor(allow=r".*?tibet.people.com.cn/\d{8}.*?"), callback="parse_item", follow=True)
    )

    @staticmethod
    def parse_item(response):
        sel = Selector(response)
        url = response.request.url
        if re.match(r'.*?tibet.people.com.cn/.*?', url):
            content = response.xpath('//html/body/div[2]/div[4]/div[1]/div[2]/div[2]/text()').extract()
            # '//*[@id="rwb_zw"]/p/text() | //*[@id="rwb_zw"]/p/strong/text()'| //*[@id="content"]/p[2]/span/span/text()
            if content:
                item = TibetNewsItem(
                    domainname='http://tibet.people.com.cn',
                    chinesename='people',
                    url=sel.root.base,
                    title=sel.css('.gq_content > h1:nth-child(2)::text').extract_first(),
                    subtitle=sel.css('.sub::text').extract_first(),
                    language='tibet',
                    encodingtype='utf-8',
                    corpustype='网络',
                    timeofpublish=sel.re(r'\d{4}.*?\d{2}.*?\d{2}.*?\d{2}:\d{2}')[0].replace('ལོའི་ཟླ་ ', '年').replace(
                        'ཚེས་', '月').replace('ཉིན།  ', '日'),
                    # timeofpublish = re.search(r'\d{4}.*？\d{2}.*?\d{2}',sel.css('.title_hd > p:nth-child(2)::text').extract_first()).group(0),
                    content=''.join(content),
                    # source=sel.css('.title_hd > p:nth-child(2)::text').extract_first(),
                    # author=sel.css('.title_hd > p:nth-child(2)::text').extract_first()
                )
                item = judge_time_tibet_news(item)
                if item:
                    yield item
