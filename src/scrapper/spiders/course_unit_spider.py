import getpass
import scrapy
from scrapy.http import Request, FormRequest
from urllib.parse import urlparse, parse_qs, urlencode
from configparser import ConfigParser, ExtendedInterpolation
from datetime import datetime
from dotenv import dotenv_values
import logging
import json

from scrapper.settings import CONFIG, PASSWORD, USERNAME

from ..database.Database import Database
from ..items import CourseUnit


class CourseUnitSpider(scrapy.Spider):
    name = "course_units"
    allowed_domains = ['sigarra.up.pt']
    login_page_base = 'https://sigarra.up.pt/feup/pt/mob_val_geral.autentica'
    password = None


    def open_config(self):
        """
        Reads and saves the configuration file. 
        """
        config_file = "./config.ini"
        self.config = ConfigParser(interpolation=ExtendedInterpolation())
        self.config.read(config_file) 

    def __init__(self, password=None, category=None, *args, **kwargs):
        super(CourseUnitSpider, self).__init__(*args, **kwargs)
        self.open_config()
        self.user = CONFIG[USERNAME]
        self.password = CONFIG[PASSWORD]
        logging.getLogger('scrapy').propagate = False

    def format_login_url(self):
        return '{}?{}'.format(self.login_page_base, urlencode({
            'pv_login': self.user,
            'pv_password': self.password
        }))

    def start_requests(self):
        "This function is called before crawling starts."
        if self.password is None:
            self.password = getpass.getpass(prompt='Password: ', stream=None)
            
        yield Request(url=self.format_login_url(), callback=self.check_login_response, errback=self.login_response_err)

    def login_response_err(self, failure):
        print('Login failed. SIGARRA\'s response: error type 404;\nerror message "{}"'.format(failure))
        print("Check your password")
    
    def check_login_response(self, response):
        """Check the response returned by a login request to see if we are
        successfully logged in. Since we used the mobile login API endpoint,
        we can just check the status code.
        """ 

        if response.status == 200:
            response_body = json.loads(response.body)
            if response_body['authenticated']:
                self.log("Successfully logged in. Let's start crawling!")
                return self.courseRequests()
           

    def courseRequests(self):
        print("Gathering courses")
        db = Database() 

        sql = "SELECT course.id, year, course.sigarra_id, faculty.acronym FROM course JOIN faculty ON course.faculty_id= faculty.acronym"
        db.cursor.execute(sql)
        self.courses = db.cursor.fetchall()
        db.connection.close()

        self.log("Crawling {} courses".format(len(self.courses)))

        for course in self.courses:
            yield scrapy.http.Request(
                url='https://sigarra.up.pt/{}/pt/ucurr_geral.pesquisa_ocorr_ucs_list?pv_ano_lectivo={}&pv_curso_id={}'.format(
                    course[3], course[1], course[2]),
                meta={'course_id': course[0]},
                callback=self.extractSearchPages)

    def extractSearchPages(self, response):
        last_page_url = response.css(
            ".paginar-saltar-barra-posicao > div:last-child > a::attr(href)").extract_first()
        last_page = int(parse_qs(urlparse(last_page_url).query)[
            'pv_num_pag'][0]) if last_page_url is not None else 1
        for x in range(1, last_page + 1):
            yield scrapy.http.Request(
                url=response.url + "&pv_num_pag={}".format(x),
                meta=response.meta,
                callback=self.extractCourseUnits)

    def extractCourseUnits(self, response):
        course_units_table = response.css("table.dados .d")
        for course_unit_row in course_units_table:
            yield scrapy.http.Request(
                url=response.urljoin(course_unit_row.css(
                    ".t > a::attr(href)").extract_first()),
                meta=response.meta,
                callback=self.extractCourseUnitInfo)

    def extractCourseUnitInfo(self, response):
        name = response.xpath(
            '//div[@id="conteudoinner"]/h1[2]/text()').extract_first().strip()

        # Checks if the course unit page is valid.
        # If name == 'Sem Resultados', then it is not.
        if name == 'Sem Resultados':
            return None  # Return None as yielding would continue the program and crash at the next assert

        course_unit_id = parse_qs(urlparse(response.url).query)[
            'pv_ocorrencia_id'][0]
        acronym = response.xpath(
            '//div[@id="conteudoinner"]/table[@class="formulario"][1]//td[text()="Sigla:"]/following-sibling::td[1]/text()').extract_first()

        # Some pages have Acronym: instead of Sigla:
        if acronym is None: 
            acronym = response.xpath(
                '//div[@id="conteudoinner"]/table[@class="formulario"][1]//td[text()="Acronym:"]/following-sibling::td[1]/text()').extract_first()

        if acronym is not None:
            acronym = acronym.replace(".", "_")

        url = response.url
        schedule_url = response.xpath(
            '//a[text()="Horário"]/@href').extract_first()

        # If there is no schedule for this course unit
        if schedule_url is not None:
            schedule_url = response.urljoin(schedule_url)

        # Occurrence has a string that contains both the year and the semester type
        occurrence = response.css('#conteudoinner > h2::text').extract_first()

        # Possible types: '1', '2', 'A', 'SP'
        # '1' and '2' represent a semester
        # 'A' represents an annual course unit
        # 'SP' represents a course unit without effect this year
        semester = occurrence[24:26].strip()

        # Represents the civil year. If the course unit is taught on the curricular year
        # 2017/2018, then year is 2017.
        year = int(occurrence[12:16])

        assert semester == '1S' or semester == '2S' or semester == 'A' or semester == 'SP' \
            or semester == '1T' or semester == '2T' or semester == '3T' or semester == '4T'

        assert year > 2000

        semesters = []

        # FIXME: Find a better way to allocate trimestral course units
        if semester == '1S' or semester == '1T' or semester == '2T':
            semesters = [1]
        elif semester == '2S' or semester == '3T' or semester == '4T':
            semesters = [2]
        elif semester == 'A':
            semesters = [1, 2]

        for semester in semesters:
            yield CourseUnit(
                sigarra_id=course_unit_id,
                course_id=response.meta['course_id'],
                name=name,
                acronym=acronym,
                url=url,
                schedule_url=schedule_url,
                year=year,
                semester=semester,
                last_updated=datetime.now()
            )
 
