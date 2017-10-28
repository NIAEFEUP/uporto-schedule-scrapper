import scrapy
from ..items import Faculty

class FacultySpider(scrapy.Spider):
    name = "faculties"

    start_urls = [
        'https://sigarra.up.pt/up/pt/web_base.gera_pagina?p_pagina=escolas'
    ]

    def parse(self, response):
        # filename = "faculdades.txt"
        # with open(filename, 'wb') as f:
        #     f.write(response.body)
        for facHtml in response.css('.menu-nivel-3 > a'):
            fac = Faculty(
                acronym = facHtml.css('::attr(href)').extract_first()[2:],
                name = facHtml.css('::attr(title)').extract_first())
            yield fac
