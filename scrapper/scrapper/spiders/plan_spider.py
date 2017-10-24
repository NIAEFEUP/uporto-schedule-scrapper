import scrapy
# from ..items import Plan
from ..con_info import ConInfo
# from urllib.parse import urlparse, parse_qs

class PlanSpider(scrapy.Spider):
    name = "plans"

    def start_requests(self):
        con_info = ConInfo()
        with con_info.connection.cursor() as cursor:
            sql = "SELECT `id`, `plan_url` FROM `course`;"
            cursor.execute(sql)
            self.courses = cursor.fetchall()
        con_info.connection.close()
        for course in self.courses:
            yield scrapy.Request(url=course[1], meta={'course_id':course[0]}, callback=self.parse)

    def parse(self, response):
        print(response.url)
        for planHtml in response.css('#anos_curr_div > .caixa'):
            course_year = planHtml.xpath("./a/text()").extract_first()
            if course_year is None:
                continue
            course_year = int(course_year[2])
            for semesterHtml in planHtml.css('table > tbody > tr > td > table > tbody > tr > td > table > tbody'):
                print(semesterHtml.extract_first())
                print(semesterHtml.css('tr > th').extract_first())
