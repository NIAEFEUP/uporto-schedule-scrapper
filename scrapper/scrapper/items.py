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
    id = scrapy.Field()
    name = scrapy.Field()
    course_type = scrapy.Field()
    faculty_id = scrapy.Field()

class FinalSchedule(scrapy.Item):
    course = scrapy.Field()
    date = scrapy.Field()
    title = scrapy.Field()
    text = scrapy.Field()
    duration = scrapy.Field()
    acronym = scrapy.Field()
    professor = scrapy.Field()
    prof_acro = scrapy.Field()
    id_class = scrapy.Field()
    location = scrapy.Field()
