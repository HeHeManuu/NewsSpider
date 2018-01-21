# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy import Field


class CrawlerItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class NewsItem(scrapy.Item):
    """ 新闻相关信息"""
    domainname = Field()
    chinesename = Field()
    language = Field()
    encodingtype = Field()
    corpustype = Field()
    filename = Field()
    title = Field()
    subtitle = Field()
    author = Field()
    timeofpublish = Field()
    timeofdownload = Field()
    localaddress = Field()
    url = Field()
    date = Field()
    content = Field()
    source = Field()
    classification = Field()
    pass


class CommentItem(scrapy.Item):
    """评论相关"""
    url = Field()
    comments = Field()
    pass



# 微博相关信息
class InformationItem(scrapy.Item):
    """ 个人信息 """
    _id = Field()  # 用户ID
    NickName = Field()  # 昵称
    Gender = Field()  # 性别
    Province = Field()  # 所在省
    City = Field()  # 所在城市
    BriefIntroduction = Field()  # 简介
    Birthday = Field()  # 生日
    Num_Tweets = Field()  # 微博数
    Num_Follows = Field()  # 关注数
    Num_Fans = Field()  # 粉丝数
    SexOrientation = Field()  # 性取向
    Sentiment = Field()  # 感情状况
    VIPLevel = Field()  # 会员等级
    Authentication = Field()  # 认证
    URL = Field()  # 首页链接


class TweetsItem(scrapy.Item):
    """ 微博信息 """
    _id = Field()  # 用户ID-微博ID
    ID = Field()  # 用户ID
    Content = Field()  # 微博内容
    PubTime = Field()  # 发表时间
    Co_oridinates = Field()  # 定位坐标
    Tools = Field()  # 发表工具/平台
    Num_Like = Field()  # 点赞数
    Num_Comment = Field()  # 评论数
    Transfer = Field()  # 转载数


class FollowsItem(scrapy.Item):
    """ 关注人列表 """
    _id = Field()  # 用户ID
    follows = Field()  # 关注


class FansItem(scrapy.Item):
    """ 粉丝列表 """
    _id = Field()  # 用户ID
    fans = Field()  # 粉丝
