
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
# 运行一个
process = CrawlerProcess(get_project_settings())

process.crawl('people_news')
process.crawl('wyxw_news')
process.crawl('xinhua_news')
# process.crawl('sina_news')
# process.crawl('qq_news')
process.crawl('zhongxin_news')
process.start()
