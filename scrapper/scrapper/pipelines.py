# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import json
import pymysql
from . import items

class ScrapperPipeline(object):
    def process_item(self, item, spider):
        return item

class JsonWriterPipeline(object):

    def open_spider(self, spider):
        self.file = open('info.json', 'w')

    def close_spider(self, spider):
        self.file.close()

    def process_item(self, item, spider):
        line = json.dumps(dict(item)) + "\n"
        self.file.write(line)
        return item

class MySQLPipeline(object):
    def __init__(self):
        self.connection = pymysql.connect(host='mysql', port=3306, user='root', passwd='root', db='tts')

    def process_item(self, item, spider):
        return item

class FacultyPipeline(MySQLPipeline):
    def __init__(self):
        MySQLPipeline.__init__(self)

    def process_item(self, item, spider):
        if not isinstance(item, items.Faculty):
            return item
        try:
            with self.connection.cursor() as cursor:
                sql = "INSERT IGNORE INTO `{0}` ({1}) VALUES('{2}')"
                cursor.execute(sql.format('faculty', ", ".join(item.keys()), "', '".join(item.values())))
                self.connection.commit()
        finally:
        	return item

class CoursePipeline(MySQLPipeline):
    def __init__(self):
        MySQLPipeline.__init__(self)

    def process_item(self, item, spider):
        if not isinstance(item, items.Faculty):
            return item
        try:
            with self.connection.cursor() as cursor:
                sql = "INSERT IGNORE INTO `{0}` ({1}) VALUES('{2}')"
                cursor.execute(sql.format('faculty', ", ".join(item.keys()), "', '".join(item.values())))
                self.connection.commit()
        finally:
        	return item
