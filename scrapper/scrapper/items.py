# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class ScrapperItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class Faculty(scrapy.Item):
    acronym = scrapy.Field()
    name = scrapy.Field()


class Course(scrapy.Item):
    course_id = scrapy.Field()
    name = scrapy.Field()
    acronym = scrapy.Field()
    course_type = scrapy.Field()
    faculty_id = scrapy.Field()
    url = scrapy.Field()
    year = scrapy.Field()
    plan_url = scrapy.Field()


class Class(scrapy.Item):
    course_id = scrapy.Field()
    year = scrapy.Field()
    acronym = scrapy.Field()
    url = scrapy.Field()


class CourseUnit(scrapy.Item):
    courseUnit_id = scrapy.Field()
    name = scrapy.Field()
    acronym = scrapy.Field()
    course_id = scrapy.Field()
    url = scrapy.Field()
    schedule_url = scrapy.Field()


class Schedule(scrapy.Item):
    courseUnit_id = scrapy.Field()
    lesson_type = scrapy.Field()  # T, TP, PL, etc.
    day = scrapy.Field()  # 0 = monday, 1 = tuesday, .., 5 = saturday (no sunday)
    duration = scrapy.Field()  # In hours: 0.5 hours is half an hour
    start_time = scrapy.Field()  # At what time the lesson starts
    teacher_acronym = scrapy.Field()  # JCF, GTD, etc.
    location = scrapy.Field()  # B001, B003, etc.
