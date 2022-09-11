
import scrapy
from datetime import datetime
from urllib.parse import urlparse, parse_qs
from configparser import ConfigParser, ExtendedInterpolation

from ..items import Course
from ..database.Database import Database

class CourseSpider(scrapy.Spider):
    name = "courses"
    allowed_domains = ['sigarra.up.pt']
    login_page = 'https://sigarra.up.pt/feup/pt/'

    start_url = "https://sigarra.up.pt/{0}/pt/cur_geral.cur_tipo_curso_view?pv_tipo_sigla={1}&pv_ano_lectivo={2}"


    def open_config(self):
        """
        Reads and saves the configuration file. 
        """
        config_file = "./config.ini"
        self.config = ConfigParser(interpolation=ExtendedInterpolation())
        self.config.read(config_file) 

    def get_year(self):
        year = self.config['default']['YEAR']
        if not year:
            raise Exception('YEAR variable not specified for parsing in configuration file!')
        return int(year)   

    def start_requests(self):

        db= Database()
        self.open_config()
        year = self.get_year()

        # TODO: reorganize this block in the Database class. 
        sql = "SELECT `id`, `acronym` FROM `faculty`;"
        db.cursor.execute(sql)
        self.faculties = db.cursor.fetchall()
        db.connection.close() 

        course_types = ['L', 'MI', 'M', 'D']
        for faculty in self.faculties:
            for course_type in course_types:
                url = self.start_url.format(faculty[1], course_type, year)
                yield scrapy.Request(url=url, meta={'faculty_id': faculty[0], 'course_type': course_type, 'year': year},
                                     callback=self.parse_get_url)

    def parse_get_url(self, response):
        for a in response.css('#conteudoinner ul#{0}_a li a:first-child'.format(response.meta['course_type'])):
            yield response.follow(a, meta=response.meta, callback=self.parse)

    def parse(self, response):
        for courseHtml in response.css('body'):
            if courseHtml.xpath(
                    '//*[@id="conteudoinner"]/div[1]/a').extract_first() is not None:  # tests if this page points to another one
                continue
            course = Course(
                course_id=int(parse_qs(urlparse(response.url).query)['pv_curso_id'][0]),
                name=courseHtml.css('#conteudoinner h1:last-of-type::text').extract_first(),
                course_type=response.meta['course_type'],
                faculty_id=response.meta['faculty_id'],
                acronym=courseHtml.css('span.pagina-atual::text').extract_first()[3:],
                url=response.url,
                plan_url=response.urljoin(courseHtml.xpath(
                    '(//h3[text()="Planos de Estudos"]/following-sibling::div[1]//a)[1]/@href').extract_first()),
                year=response.meta['year'],
                last_updated=datetime.now()
            )
            yield course
