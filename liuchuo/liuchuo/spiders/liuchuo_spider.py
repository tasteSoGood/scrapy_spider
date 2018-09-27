import scrapy
from liuchuo.items import LiuchuoItem

class liuchuo_spider(scrapy.Spider):
    name = "liuchuo"
    allowed_domains = []
    start_urls = [
        "https://www.liuchuo.net/archives/6613"
    ]

    def parse(self, response):
        item = LiuchuoItem()
        item['blog_id'] = response.url.split('/')[-1]
        try:
            item['title'] = response.xpath('.//article/header/h1[@class="entry-title"]/text()').extract()[0]
        except:
            item['title'] = "无标题"
        content = response.xpath('.//article/div[@class="entry-content"]/p').extract()
        item['content'] = ''
        for _ in content:
            item['content'] += _
        item['time'] = response.xpath('.//article/footer/span/a/time/@datetime').extract()[0]
        yield item
        
        next_url = response.xpath('.//div[@class="nav-previous"]/a/@href').extract()[0]
        yield scrapy.http.Request(url = next_url, callback = self.parse)
        # 在爬取的时候,有可能会与allowed_domains产生冲突,这个时候需要使用dont_filter属性禁用该功能
        # 但是,allowed_domains可以防止爬虫无限制地访问,最好的解决方法还是要从根源上开始
