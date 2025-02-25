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
    name = scrapy.Field()
    acronym = scrapy.Field()
    last_updated = scrapy.Field()
    recent_occr = scrapy.Field()

class CourseCourseUnit(scrapy.Item):
    course_id = scrapy.Field()
    course_unit_id = scrapy.Field()
    year = scrapy.Field()
    semester = scrapy.Field()
    ects = scrapy.Field()
    
class CourseUnitProfessor(scrapy.Item):
    course_unit_id = scrapy.Field()
    professor_id = scrapy.Field()
    
class Professor(scrapy.Item):
    id = scrapy.Field()
    name = scrapy.Field()
