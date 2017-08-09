
from scrapy.crawler import CrawlerProcess
from Crawler.spiders import PeopleNewsSpider
from Crawler.spiders import NewsSpider
from scrapy.utils.project import get_project_settings
# 运行一个
process = CrawlerProcess(get_project_settings())

process.crawl('people_news')
process.crawl('wyxw_news')
process.crawl('xinhua_news')
process.start()
