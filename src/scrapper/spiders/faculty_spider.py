from re import A
import scrapy

from ..items import Faculty
from datetime import datetime

class FacultySpider(scrapy.Spider):
    name = "faculties"

    start_urls = [
        'https://sigarra.up.pt/up/pt/web_base.gera_pagina?p_pagina=escolas'
    ]

    faculty_special_cases = {
        "https://www.esenf.pt/pt/": "esep"
    }

    def extract_faculty_name(self, href):
        if href in self.faculty_special_cases:
            return self.faculty_special_cases[href]
        
        return href.split("/")[-2]

    def parse(self, response):
        for facHtml in response.css('.component-margin.hot-links a'):
            yield Faculty(
                acronym=self.extract_faculty_name(facHtml.css('::attr(href)').extract_first()),
                name=facHtml.css('::text').extract_first(),
                last_updated=datetime.now()
            )

        
