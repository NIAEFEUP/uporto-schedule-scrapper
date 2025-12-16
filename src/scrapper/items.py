# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class Faculty(scrapy.Item):
    acronym = scrapy.Field()
    name = scrapy.Field()
    last_updated = scrapy.Field()

class Course(scrapy.Item):
    id = scrapy.Field()
    faculty_id = scrapy.Field()
    name = scrapy.Field()
    acronym = scrapy.Field()
    course_type = scrapy.Field()
    url = scrapy.Field()
    year = scrapy.Field()
    plan_url = scrapy.Field()
    last_updated = scrapy.Field()

class CourseUnit(scrapy.Item):
    id = scrapy.Field()
    course_id = scrapy.Field()
    name = scrapy.Field()
    acronym = scrapy.Field()
    url = scrapy.Field()
    semester = scrapy.Field()
    year = scrapy.Field()
    schedule_url = scrapy.Field()
    classes_url = scrapy.Field()
    last_updated = scrapy.Field()
    hash = scrapy.Field()
    course_group = scrapy.Field()

class CourseMetadata(scrapy.Item):
    course_id = scrapy.Field()
    course_unit_id = scrapy.Field()
    course_unit_year = scrapy.Field()
    ects = scrapy.Field()

class CourseGroup(scrapy.Item):
    id = scrapy.Field()
    name = scrapy.Field()
    course_id = scrapy.Field()
    year = scrapy.Field()
    semester = scrapy.Field()
    
class CourseUnitGroup(scrapy.Item):
    course_unit_id = scrapy.Field()
    course_group_id =scrapy.Field()

