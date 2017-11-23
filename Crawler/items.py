# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class CrawlerItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class NewsItem(scrapy.Item):
    domainname = scrapy.Field()
    chinesename = scrapy.Field()
    language = scrapy.Field()
    encodingtype = scrapy.Field()
    corpustype = scrapy.Field()
    filename = scrapy.Field()
    title = scrapy.Field()
    subtitle = scrapy.Field()
    author = scrapy.Field()
    timeofpublish = scrapy.Field()
    timeofdownload = scrapy.Field()
    localaddress = scrapy.Field()
    url = scrapy.Field()
    content = scrapy.Field()
    source = scrapy.Field()
    classification = scrapy.Field()
    pass


class WeiboItem(scrapy.Item):
    author = scrapy.Field()
    content = scrapy.Field()
    num_forwarding = scrapy.Field()
    num_comment = scrapy.Field()
    num_likes = scrapy.Field()
