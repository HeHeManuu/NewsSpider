# -*- coding: utf-8 -*-

import scrapy
from scrapy.spiders import CrawlSpider
from scrapy.spiders import Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.selector import Selector
from Crawler.items import NewsItem
from Crawler.utils import *
import re
import Crawler.settings



class UyghurpeoplenewsspiderSpider(CrawlSpider):
    name = 'uyghur_people_news'
    allowed_domains = [
    					'uyghur.people.com.cn'
    				  ]

    start_urls = [
    	'http://uyghur.people.com.cn/'
    ]
    
    rules = (
        Rule(LinkExtractor(allow=".*?.uyghur.people.com.cn.*?", deny=r'.*?.uyghur.people.com.cn.*?/\d{6}/.*?'), follow=True),
        Rule(LinkExtractor(allow='.*?/\d{6}/.*?'), callback="parse_item", follow=True)
    )

    @staticmethod
    def parse_item(response):
        sel = Selector(response)
        url = response.request.url
        if re.match(r'.*?people.com.cn.*?/\d+/.*?', url) and 'BIG' not in url:
            content = response.xpath('//*[@id="p_content"]/span/text() | //*[@class="clearfix"]/p/text()').extract()
            if content:
                item = NewsItem(
                    domainname='http://uyghur.people.com.cn/',
                    chinesename='维语人民网',
                    url=sel.root.base,
                    title=sel.css('div.ej_right > h1::text').extract_first(),
                    subtitle=sel.css('div.ej_right > h5::text').extract_first(),
                    language='维文',
                    encodingtype='utf-8',
                    corpustype='网络',
                    # timeofpublish=sel.re(
                    #     r'\d{4}年\d{2}月\d{2}日\d{2}:\d{2}')[0],
                    timeofpublish=sel.css('div.ej_right #p_publishtime::text').extract_first(),
                    content=''.join(content),
                    source=sel.css('div.ej_right #p_origin > a:nth-child(1)::text').extract_first(),
                    author=sel.css('div.ej_right #p_publishtime::text').extract_first()

                )
                print(item.get("title", None))
                print(item.get("timeofpublish", None))
                print(item.get("source", None))
                print(item.get("author",None))
                item = judge_time_tibet_news(item)
                if item:
                    yield item
