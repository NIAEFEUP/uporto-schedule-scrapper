import scrapy

from ..items import Faculty

class FacultiesSpider(scrapy.Spider):
    name = "faculties"
    allowed_domains = ["sigarra.up.pt"]

    start_urls = [
        "https://sigarra.up.pt/up/pt/web_base.gera_pagina?p_pagina=escolas"
    ]

    def parse(self, response):
        for faculty in response.css("ul > li.menu-nivel-3 > a"):
            acronym = faculty.attrib['href'][2:]
            name = faculty.css("::text").get()
            # self.logger.debug("{} - {}".format(acronym, name))

            yield Faculty(
                name=name,
                acronym=acronym,
            )
