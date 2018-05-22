from scrapy.spiders import CrawlSpider
from scrapy.spiders import Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.selector import Selector
from scrapy.http import Request
from Crawler.items import NewsItem, CommentItem
from Crawler.utils import judge_time_news, get_allow_date
from Crawler.settings import *
import re
import requests
import json


def get_163_allow_url():
    """
    获得允许的url匹配,通过日期匹配
    :return: 
    """
    start_time = NOW - datetime.timedelta(END_DAY)
    allow_url = list()
    if END_DAY < 21:
        return get_allow_date('%y/%m%d')
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
    allowed_domains = ["news.163.com", "sports.163.com", "money.163.com", 'edu.163.com', "tech.163.com", "war.163.com"]

    start_urls = [
        'http://news.163.com',
        'http://news.163.com/special/0001386F/rank_news.html',
        "http://money.163.com/",
        "http://sports.163.com",
        "http://tech.163.com/",
        "http://edu.163.com/",
        "http://war.163.com/"
    ]
    deny_urls = [
        r'.*?news.163.com.*?/\d{2}/\d{4}/.*?',
        r'.*?.photo.*?',
        r'.*?.video.*?',
        r'.*?.picstory.*?',
        r'.*?reviews.*?'
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

    def parse_item(self, response):
        sel = Selector(response)
        url = response.request.url
        if re.match(r'.*?163.com.*?/\d+/\d+/.*?', url):
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
                    if GET_COMMENTS:
                        comment = self.get_comments(url)
                        if comment:
                            yield comment

    def get_comments(self, news_url):
        s1 = 'http://comment.news.163.com/api/v1/products/a2869674571f77b5a0867c3d71db5856/threads/'
        s2 = '/comments/newList?offset='
        s3 = '&limit='
        news_id = news_url.split('/')[-1].split('.')[0]
        s = s1 + news_id + s2

        all_comments = []

        offset, limit = 0, 40
        while offset < limit:
            url = s + str(offset) + s3 + str(40)
            res = requests.get(url=url).text
            if res is None:
                break
            data = json.loads(res)
            if offset == 0:
                if 'newListSize' not in data:
                    break
                limit = data['newListSize']
            for k, v in data['comments'].items():
                per_comment = dict()
                per_comment['against'] = v['against']
                per_comment['vote'] = v['vote']
                per_comment['time'] = v['createTime']
                per_comment['content'] = v['content']
                per_comment['location'] = v['user']['location']
                per_comment['nick'] = '' if 'nickname' not in v['user'] else v['user']['nickname']
                all_comments.append(per_comment)
            offset += 40
        if len(all_comments) == 0 or limit == 0:
            return None
        comment_item = CommentItem(
            url=news_url,
            sitename='NetEase',
            num_comments=len(all_comments),
            comments=all_comments
        )
        return comment_item
