
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
# 运行一个
process = CrawlerProcess(get_project_settings())

process.crawl('wyxw_comments')
process.crawl('sina_comments')
process.crawl('qq_comments')
process.start()
