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
        for planHtml in response.xpath('//*[@id="anos_curr_div"]/div[a]'):
            course_year = planHtml.xpath("./a/text()").extract_first()
            print(response.meta['course_name'] + ' - ' + course_year)

            classes = defaultdict(list)
            for table in planHtml.xpath('.//table/tr/td/table/tr/td/table'):
                semester = table.xpath('./tr/th/text()').extract_first()
                for class_line in table.xpath('./tr[td/a and string-length(./td[1]/text()) > 0]'):
                    class_info_node = class_line.xpath('./td')
                    class_info = {
                        'code': class_info_node[0].xpath('./text()').extract_first(),
                        'acronym': class_info_node[1].xpath('./text()').extract_first(),
                        'name': class_info_node[2].xpath('./a/text()').extract_first(),
                        'class_url': response.urljoin(class_info_node[2].xpath('./a/@href').extract_first())
                    }
                    print(class_info)
                    classes[course_year + '-' + semester].append(class_info)
            
