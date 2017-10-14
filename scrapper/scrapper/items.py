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
