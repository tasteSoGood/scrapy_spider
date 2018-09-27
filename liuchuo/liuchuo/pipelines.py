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
import pymysql as mysql

class LiuchuoPipeline(object):
    def __init__(self):
        self.item_pool = set()
        self.db_con = mysql.connect(
            host = 'localhost',
            user = 'root',
            password = '123456',
            db = 'LIUCHUO'
        )
        self.cursor = self.db_con.cursor()
        self.temp_execute = []

    def open_spider(self, spider): 
        if not self.cursor.execute("SHOW TABLES LIKE 'blog';"):
            # 创建表
            sql = """\
            CREATE TABLE blog(\
                id INT AUTO_INCREMENT NOT NULL,\
                blog_id INT NOT NULL,\
                time VARCHAR(50),\
                title VARCHAR(1000),\
                path VARCHAR(1000),\
                PRIMARY KEY(id)\
            )AUTO_INCREMENT = 1 DEFAULT CHARSET = utf8; \
            """
            self.cursor.execute(sql)
        else:
            # 提取键值
            sql = """\
            SELECT blog_id FROM blog;\
            """
            self.cursor.execute(sql)
            data = self.cursor.fetchall()
            self.item_pool = {i[0] for i in data}

    def process_item(self, item, spider):
        # 该方法只能返回一个item对象或者抛出DropItem错误
        item['title'] = self.content_filter(item['title'])
        item['content'] = self.content_filter(item['content'])
        if item['blog_id'] not in self.item_pool:
            if len(self.temp_execute) < 200:
                path = "./blog_data/{0}: {1}.txt".format(item['blog_id'], item['title'])
                with open(path, 'w') as f:
                    f.write(item['content'])
                self.temp_execute.append((item['blog_id'], item['time'], item['title'], path))
            else:
                sql = """\
                INSERT INTO blog(blog_id, time, title, path)\
                VALUES (%s, %s, %s, %s);\
                """
                self.cursor.executemany(sql, self.temp_execute)
                self.db_con.commit()
                self.temp_execute = []
            self.item_pool.add(item['blog_id'])
            return item
        else:
            raise DropItem("This blog have been visited.")

    def close_spider(self, spider):
        if len(self.temp_execute):
            # 扫尾
            sql = """\
            INSERT INTO blog(blog_id, time, title, path)\
            VALUES (%s, %s, %s, %s);\
            """
            self.cursor.executemany(sql, self.temp_execute)
            self.db_con.commit()
        self.cursor.close()
        self.db_con.close()
    
    def content_filter(self, string):
        res = string.replace('\n', '')
        res = res.replace('\t', '')
        res = res.replace('\r', '')
        res = res.replace('"', '\"')
        res = res.replace("'", "\'")
        res = res.replace('\\', "\\\\")
        return res