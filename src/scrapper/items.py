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
    faculty_id = scrapy.Field()
    sigarra_id = scrapy.Field()
    name = scrapy.Field()
    acronym = scrapy.Field()
    course_type = scrapy.Field()
    url = scrapy.Field()
    year = scrapy.Field()
    plan_url = scrapy.Field()
    last_updated = scrapy.Field()


class CourseUnit(scrapy.Item):
    sigarra_id = scrapy.Field()
    course_id = scrapy.Field()
    name = scrapy.Field()
    acronym = scrapy.Field()
    url = scrapy.Field()
    semester = scrapy.Field()
    year = scrapy.Field()
    schedule_url = scrapy.Field()
    last_updated = scrapy.Field()

class CourseMetadata(scrapy.Item):
    course_id = scrapy.Field()
    course_unit_id = scrapy.Field()
    course_unit_year = scrapy.Field()
    ects = scrapy.Field()

class Schedule(scrapy.Item):
    course_unit_id = scrapy.Field()
    lesson_type = scrapy.Field()  # T, TP, PL, etc.
    day = scrapy.Field()  # 0 = monday, 1 = tuesday, .., 5 = saturday (no sunday)
    duration = scrapy.Field()  # In hours: 0.5 hours is half an hour
    start_time = scrapy.Field()  # At what time the lesson starts
    is_composed = scrapy.Field()
    professor_sigarra_id = scrapy.Field()
    location = scrapy.Field()  # B001, B003, etc.
    class_name = scrapy.Field()  # 1MIEIC01
    composed_class_name = scrapy.Field()  # None or COMP_372
    last_updated = scrapy.Field()
    
class ScheduleProfessor(scrapy.Item):
    schedule_id = scrapy.Field()
    professor_sigarra_id = scrapy.Field()

class Professor(scrapy.Item):
    sigarra_id = scrapy.Field()
    professor_acronym = scrapy.Field()
    professor_name = scrapy.Field()
    