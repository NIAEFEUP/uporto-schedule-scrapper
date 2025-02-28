from re import A
import scrapy

from ..items import Faculty
from datetime import datetime
from scrapper.settings import ONLY_FEUP

class FacultySpider(scrapy.Spider):
    name = "faculties"

    start_urls = [
        'https://sigarra.up.pt/up/pt/web_base.gera_pagina?p_pagina=escolas'
    ]

    def parse(self, response):
        print(ONLY_FEUP)
        for facHtml in response.css('.component-margin.hot-links a'):
             if( ONLY_FEUP and facHtml.css('::attr(href)').extract_first().split("/")[-2] == "feup"):
                yield Faculty(
                    acronym=facHtml.css('::attr(href)').extract_first().split("/")[-2],
                    name=facHtml.css('::text').extract_first(),
                    last_updated=datetime.now()
                )

        