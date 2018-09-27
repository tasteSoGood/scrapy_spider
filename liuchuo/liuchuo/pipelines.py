# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
# Scrapy的运行顺序是这样的: items作为项目的限定, 在几个子线程中传递, 在
# spider运行的时候, 捕捉到的items传递给pipeline做处理, spider和pipelines
# 属于并行的两个线程, 是生产者和消费者的关系. 当然, 在没有items的情况下, 
# 或者没有pipeline的情况下, spider都可以正确地运行

from scrapy.exceptions import DropItem
import json

class LiuchuoPipeline(object):
    def __init__(self):
        self.item_pool = dict()

    def open_spider(self, spider):
        pass

    def process_item(self, item, spider):
        # 该方法只能返回一个item对象或者抛出DropItem错误
        if item['blog_id'] not in self.item_pool:
            self.item_pool[item['blog_id']] = {
                'title': item['title'],
                'time': item['time'],
                'content': self.content_filter(item['content'])
            }
            return item
        else:
            raise DropItem("This blog have been visited.")

    def close_spider(self, spider):
        with open('items.json', 'w') as f:
            f.write(json.dumps(self.item_pool, indent = 4, ensure_ascii = False))
    
    def content_filter(self, string):
        res = string.replace('\n', '')
        res = res.replace('\t', '')
        res = res.replace('\r', '')
        return res