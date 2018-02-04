# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import json
import pymysql
from . import items
from .con_info import ConInfo


class MySQLPipeline(ConInfo):
    def process_item(self, item, spider):
        return item


class FacultyPipeline(MySQLPipeline):
    def __init__(self):
        MySQLPipeline.__init__(self)

    def process_item(self, item, spider):
        if not isinstance(item, items.Faculty):
            return item
        sql = "INSERT INTO `{0}` (`{1}`) VALUES ({2})"
        prepared = sql.format('faculty', "`, `".join(item.keys()), ", ".join("%s" for _ in item.values()))
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(prepared, tuple(item.values()))
                self.connection.commit()
        finally:
            return item


class CoursePipeline(MySQLPipeline):
    def __init__(self):
        MySQLPipeline.__init__(self)

    def process_item(self, item, spider):
        if not isinstance(item, items.Course):
            return item
        sql = "INSERT INTO `{0}` (`{1}`) VALUES ({2})"
        columns = "`, `".join(item.keys())
        values = ", ".join("%s" for _ in item.values())
        prepared = sql.format('course', columns, values)
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(prepared, tuple(item.values()))
                self.connection.commit()
        finally:
            return item


class CourseUnitPipeline(MySQLPipeline):
    def __init__(self):
        MySQLPipeline.__init__(self)

    def process_item(self, item, spider):
        if not isinstance(item, items.CourseUnit):
            return item
        sql = "INSERT INTO `{0}` (`{1}`) VALUES ({2})"
        columns = "`, `".join(key for key in item.keys())
        values = ", ".join("%s" for _ in item.values())
        prepared = sql.format('course_unit', columns, values)
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(prepared, tuple(item.values()))
                self.connection.commit()
        finally:
            return item


class SchedulePipeline(MySQLPipeline):
    def __init__(self):
        MySQLPipeline.__init__(self)

    def process_item(self, item, spider):
        if not isinstance(item, items.Schedule):
            return item
        sql = "INSERT INTO `{0}` (`{1}`) VALUES ({2})"
        columns = "`, `".join(item.keys())
        values = ", ".join("%s" for _ in item.values())
        prepared = sql.format('schedule', columns, values)
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(prepared, tuple(item.values()))
                self.connection.commit()
        finally:
            return item
