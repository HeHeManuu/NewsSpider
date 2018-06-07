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

class UyghurcctvspiderSpider(CrawlSpider):
    name = 'uyghur_cctv'
    # allowed_domains = [
    # 					'uyghur.cctv.com',
    #                     'uyghur.cctv.cn',
    #                     'uyghur.cctv.com/medeniyet/whnews',
    #                     'uyghur.cctv.com/sports',
    #                     'uyghur.cctv.com/kejiao/home'
    # 				  ]
    start_urls = [
        # 'http://uyghur.cctv.com/',
        # 'http://uyghur.cctv.com/medeniyet/whnews/',
        # 'http://uyghur.cctv.com/sports/',
        # 'http://uyghur.cctv.com/kejiao/home/'
        # 'http://uyghur.cctv.com/2017/11/08/ARTITDh1mOiCfZRb79NZqjlJ171108.shtml'
        'http://uyghur.cctv.com/sports/',
        'http://uyghur.cctv.com/medeniyet/whnews/',
        'http://uyghur.cctv.com/kejiao/home/'
    ]

    rules = (
        Rule(LinkExtractor(allow=r".*?.uyghur.cctv.com.*?", deny=r'.*?/\d{4}/\d{2}/\d{2}/.*?'), follow=True),
        Rule(LinkExtractor(allow=r".*?/\d{4}/\d{2}/\d{2}/.*?"), callback="parse_item", follow=True)
    )

    @staticmethod
    def parse_item(response):
        sel = Selector(response)
        print(sel)
        url = response.request.url
        if re.match(r'.*?/\d{4}/\d{2}/\d{2}/.*?', url):
            print('---------------------')
            print(url)
            content = response.xpath('//*[@id="page_body"]/div[2]/div/div[1]/div[1]/div/div[2]/p[2]/text() | //*[@id="page_body"]/div[2]/div/div[1]/div[1]/div/div[2]/p[2]/span/text()').extract()
                                   # '//*[@id="rwb_zw"]/p/text() | //*[@id="rwb_zw"]/p/strong/text()'| //*[@id="content"]/p[2]/span/span/text()
            print(content)
            if content:
                item = NewsItem(
                    domainname='http://uyghur.cntv.com',
                    chinesename='CCTV',
                    url=sel.root.base,
                    title=sel.css('.title_hd > h3:nth-child(1)::text').extract_first(),
                    subtitle=sel.css('.sub::text').extract_first(),
                    language='中文',
                    encodingtype='utf-8',
                    corpustype='网络',
                    # timeofpublish=sel.re(r'\d{4}_\d{2}_\d{2}')[0],
                    # strr=sel.css('.title_hd > p:nth-child(2)::text').extract_first(),
                    timeofpublish = re.search(r'\d{2}-\d{2}-\d{4}',sel.css('.title_hd > p:nth-child(2)::text').extract_first()).group(0),
                    content=''.join(content),
                    # source=sel.css('.title_hd > p:nth-child(2)::text').extract_first(),
                    # author=sel.css('.title_hd > p:nth-child(2)::text').extract_first()
                )
                print(item.get("title", None))
                print(item.get("timeofpublish", None))
                print(item.get("source", None))
                print(item.get("author", None))
                item = judge_time_tibet_news(item)
                if item:
                    yield item