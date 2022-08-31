# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import json
import pymysql
from . import items
from .con_info import ConInfo
from configparser import ConfigParser, ExtendedInterpolation

config_file = "./config.ini"
config = ConfigParser(interpolation=ExtendedInterpolation())
config.read(config_file)


class MySQLPipeline(ConInfo):
    def process_item(self, item, spider):
        return item

    """
        Saves the scrapped information in a specific file, so it can be easily exported. 
    """
    def save2file(self, item, prepared):
        try:
            values = tuple(map(lambda x: "\'{}\'".format(x), item.values()))
            self.sql_file.write(prepared % values + ";\n")           
        except Exception as e:
            print(e)


class FacultyPipeline(MySQLPipeline):
    def __init__(self):
        MySQLPipeline.__init__(self)
        self.sql_file = open(config['files']['faculty'], 'a')

    def process_item(self, item, spider):
        if not isinstance(item, items.Faculty):
            return item
        sql = "INSERT INTO `{0}` (`{1}`) VALUES ({2})"
        prepared = sql.format('faculty', "`, `".join(item.keys()), ", ".join("%s" for _ in item.values()))
        self.save2file(item, prepared)
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(prepared, tuple(item.values()))
                self.connection.commit()
        except Exception as e:
            print(e)
        finally:
            return item


class CoursePipeline(MySQLPipeline):
    def __init__(self):
        MySQLPipeline.__init__(self)
        self.sql_file = open(config['files']['course'], 'a')

    def process_item(self, item, spider):
        if not isinstance(item, items.Course):
            return item
        sql = "INSERT INTO `{0}` (`{1}`) VALUES ({2})"
        columns = "`, `".join(item.keys())
        values = ", ".join("%s" for _ in item.values())
        prepared = sql.format('course', columns, values)
        self.save2file(item, prepared)
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(prepared, tuple(item.values()))
                self.connection.commit()
        except Exception as e:
            print(e)
        finally:
            return item


class CourseUnitPipeline(MySQLPipeline):
    def __init__(self):
        MySQLPipeline.__init__(self)
        self.sql_file = open(config['files']['course_unit'], 'a')

    def process_item(self, item, spider):
        if not isinstance(item, items.CourseUnit):
            return item
        sql = "INSERT INTO `{0}` (`{1}`) VALUES ({2})"
        columns = "`, `".join(key for key in item.keys())
        values = ", ".join("%s" for _ in item.values())
        prepared = sql.format('course_unit', columns, values)
        self.save2file(item, prepared)
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(prepared, tuple(item.values()))
                self.connection.commit()
        except Exception as e:
            print(e)
        finally:
            return item


class SchedulePipeline(MySQLPipeline):
    def __init__(self):
        MySQLPipeline.__init__(self)
        self.sql_file = open(config['files']['schedule'], 'a')

    def process_item(self, item, spider):
        if not isinstance(item, items.Schedule):
            return item
        sql = "INSERT INTO `{0}` (`{1}`) VALUES ({2})"
        columns = "`, `".join(item.keys())
        values = ", ".join("%s" for _ in item.values())
        prepared = sql.format('schedule', columns, values)
        self.save2file(item, prepared)
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(prepared, tuple(item.values()))
                self.connection.commit()
        except Exception as e:
            print(e)
        finally:
            return item
