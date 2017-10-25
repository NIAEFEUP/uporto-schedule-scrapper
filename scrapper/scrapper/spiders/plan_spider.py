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
        # css alternative for below: #anos_curr_div > .caixa
        for planHtml in response.xpath('//*[@id="anos_curr_div"]/div'):
            course_year = planHtml.xpath("./a/text()").extract_first()
            if course_year is None:
                continue
            course_year = int(course_year[2])
            # css alternative for below: table > tbody > tr:first-child > td > table > tbody > tr > td > table > tbody
            for semesterHtml in planHtml.xpath('//table/tbody/tr[1]/td/table/tbody/tr/td/table/tbody'):
                print(semesterHtml.extract_first())
                print(semesterHtml.css('tr > th').extract_first())

        # TODO: test css/xpath selectors for the page example in scrapy shell to determine what is wrong
        # example page is dumped and url is in the README example
