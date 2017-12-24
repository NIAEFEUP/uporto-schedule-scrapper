import scrapy
from ..con_info import ConInfo
from collections import defaultdict

class PlanSpider(scrapy.Spider):
    name = "plans"

    def start_requests(self):
        con_info = ConInfo()
        with con_info.connection.cursor() as cursor:
            sql = "SELECT `id`, `plan_url`, `name` FROM `course` LIMIT 1"
            cursor.execute(sql)
            self.courses = cursor.fetchall()
        con_info.connection.close()
        for course in self.courses:
            yield scrapy.Request(url=course[1], meta={'course_id':course[0], 'course_name':course[2]}, callback=self.parse)

    def parse(self, response):
        con_info = ConInfo()
        for planHtml in response.xpath('//*[@id="anos_curr_div"]/div[a]'):

            # strip whitespaces and get only the first char, which represents the year
            course_year = planHtml.xpath("./a/text()").extract_first().strip()[:1]

            for table in planHtml.xpath('.//table/tr/td/table/tr/td/table'):

                # semester may be '1', '2' or 'A', where A means the class is annual
                semester = table.xpath('./tr/th/text()').extract_first()[:1]

                for class_line in table.xpath('./tr[td/a and string-length(./td[1]/text()) > 0]'):
                    class_info_node = class_line.xpath('./td')
                    class_info = {
                        'code': class_info_node[0].xpath('./text()').extract_first(),
                        'acronym': class_info_node[1].xpath('./text()').extract_first(),
                        'name': class_info_node[2].xpath('./a/text()').extract_first(),
                        'class_url': response.urljoin(class_info_node[2].xpath('./a/@href').extract_first())
                    }

                    with con_info.connection.cursor() as cursor:
                        sql = "INSERT INTO class(`year`, `acronym`, `url`, `course_id`) VALUES(%s, %s, %s, %s)"
                        cursor.execute(sql, (course_year, class_info['acronym'], class_info['class_url'], response.meta['course_id']))

        con_info.connection.commit() # commit the changes

