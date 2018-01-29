import scrapy

from ..items import Faculty
from datetime import datetime


class FacultySpider(scrapy.Spider):
    name = "faculties"

    start_urls = [
        'https://sigarra.up.pt/up/pt/web_base.gera_pagina?p_pagina=escolas'
    ]

    def parse(self, response):
        for facHtml in response.css('.menu-nivel-3 > a'):
            yield Faculty(
                acronym=facHtml.css('::attr(href)').extract_first()[2:],
                name=facHtml.css('::attr(title)').extract_first(),
                last_updated=datetime.now()
            )
