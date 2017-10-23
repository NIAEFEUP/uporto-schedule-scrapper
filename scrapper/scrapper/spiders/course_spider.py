import scrapy
from ..items import Course
from .. import con_info
from urllib.parse import urlparse, parse_qs

class CourseSpider(scrapy.Spider):
    name = "courses"

    start_url = "https://sigarra.up.pt/{0}/pt/cur_geral.cur_tipo_curso_view?pv_tipo_sigla={1}&pv_ano_lectivo={2}"

    with con_info.connection.cursor() as cursor:
        sql = "SELECT `id`, `acronym` FROM `faculty`;"
        cursor.execute(sql)
        faculties = cursor.fetchall()

    con_info.connection.close()

    def start_requests(self):
        course_types = ['L', 'MI', 'M', 'D'];
        for faculty in self.faculties:
            for course_type in course_types:
                url = self.start_url.format(faculty[1], course_type, '2017')
                yield scrapy.Request(url=url, meta={'faculty':faculty, 'course_type':course_type}, callback=self.parse)

    def parse(self, response):
        for courseHtml in response.css('#conteudoinner ul#{0}_a li a:first-child'.format(response.meta['course_type'])):
            course = Course(
		id = parse_qs(urlparse(courseHtml.css('::attr(href)').extract_first()).query)['pv_curso_id'][0],
                name = courseHtml.css('::text').extract_first(),
                course_type = response.meta['course_type'],
                faculty_id = response.meta['faculty'][0])
            print(course, response.meta['faculty'][1])
