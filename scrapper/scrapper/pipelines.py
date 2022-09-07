# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import json
from . import items
from configparser import ConfigParser, ExtendedInterpolation
from .database.Database import Database

config_file = "./config.ini"
config = ConfigParser(interpolation=ExtendedInterpolation())
config.read(config_file)

class MySQLPipeline():
    def __init__(self): 
        self.db = Database()

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

    def process_item(self, item, spider):
        if isinstance(item, items.Faculty):
            self.db.insert_faculty(list(item.values()))
        return item 


class CoursePipeline(MySQLPipeline):
    def __init__(self):
        MySQLPipeline.__init__(self)

    def process_item(self, item, spider):
        if isinstance(item, items.Course):
            self.db.insert_course(list(item.values()))
        return item 

class CourseUnitPipeline(MySQLPipeline):
    def __init__(self):
        MySQLPipeline.__init__(self)

    def process_item(self, item, spider):
        if isinstance(item, items.CourseUnit):
            self.db.insert_course_unit(list(item.values()))
        return item


class SchedulePipeline(MySQLPipeline):
    def __init__(self):
        MySQLPipeline.__init__(self)

    def process_item(self, item, spider):
        if isinstance(item, items.Schedule):
            self.db.insert_schedule(list(item.values()))
        return item
     