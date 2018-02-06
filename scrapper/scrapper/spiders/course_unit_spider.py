import getpass
import scrapy
from scrapy.http import Request, FormRequest
from urllib.parse import urlparse, parse_qs
from datetime import datetime

from ..con_info import ConInfo
from ..items import CourseUnit


class CourseUnitSpider(scrapy.Spider):
    name = "course_units"
    allowed_domains = ['sigarra.up.pt']
    login_page = 'https://sigarra.up.pt/'
    password = None

    def __init__(self, category=None, *args, **kwargs):
        super(CourseUnitSpider, self).__init__(*args, **kwargs)

    def start_requests(self):
        """This function is called before crawling starts."""
        yield Request(url=self.login_page, callback=self.login)

    def login(self, response):
        """Generate a login request. The login form needs the following parameters:
            p_app : 162 -> This is always 162
            p_amo : 55 -> This is always 55
            p_address : WEB_PAGE.INICIAL -> This is always 'WEB_PAGE.INICIAL'
            p_user : username -> This is the username used to login
            p_pass : password -> This is the password used to login
        """

        if self.password is None:
            self.password = getpass.getpass(prompt='Password: ', stream=None)

        yield FormRequest.from_response(response,
                                        formdata={
                                            'p_app': '162', 'p_amo': '55',
                                            'p_address': 'WEB_PAGE.INICIAL',
                                            'p_user': self.user,
                                            'p_pass': self.password},
                                        callback=self.check_login_response)

    def check_login_response(self, response):
        """Check the response returned by a login request to see if we are
        successfully logged in. It is done by checking if a button's value is
        'Terminar sessão', that translates to 'Sign out', meaning the login was successful.
        It also verifies if the login failed due to incorrect credentials, in case the button's
        value equals 'Iniciar sessão', that translates to 'Sign in',
        meaning the credentials were wrong or due to a change in website structure.
        """
        result = response.xpath(
            '//div[@id="caixa-validacao-conteudo"]/button[@type="submit"]/@value').extract_first()

        if result == "Terminar sessão":
            self.log("Successfully logged in. Let's start crawling!")
            # Spider will now call the parse method with a request
            return self.courseRequests()
        elif result == "Iniciar sessão":
            print('Login failed. Please try again.')
            self.log('Login failed. Please try again.')
        else:
            print('Unexpected result. Website structure may have changed.')
            self.log('Unexpected result. Website structure may have changed.')

    def courseRequests(self):
        self.log("Gathering courses")
        con_info = ConInfo()
        with con_info.connection.cursor() as cursor:
            sql = "SELECT course.id, year, course.course_id, faculty.acronym FROM course JOIN faculty ON course.faculty_id = faculty.id"
            cursor.execute(sql)
            self.courses = cursor.fetchall()
        con_info.connection.close()
        self.log("Crawling {} courses".format(len(self.courses)))

        for course in self.courses:

            yield scrapy.http.Request(
                url='https://sigarra.up.pt/{}/pt/ucurr_geral.pesquisa_ocorr_ucs_list?pv_ano_lectivo={}&pv_curso_id={}'.format(
                    course[3], course[1], course[2]),
                meta={'course_id': course[0]},
                callback=self.extractSearchPages)

    def extractSearchPages(self, response):
        last_page_url = response.css(".paginar-saltar-barra-posicao > div:last-child > a::attr(href)").extract_first()
        last_page = int(parse_qs(urlparse(last_page_url).query)['pv_num_pag'][0]) if last_page_url is not None else 1
        for x in range(1, last_page + 1):
            yield scrapy.http.Request(
                url=response.url + "&pv_num_pag={}".format(x),
                meta=response.meta,
                callback=self.extractCourseUnits)

    def extractCourseUnits(self, response):
        course_units_table = response.css("table.dados .d")
        for course_unit_row in course_units_table:
            yield scrapy.http.Request(
                url=response.urljoin(course_unit_row.css(".t > a::attr(href)").extract_first()),
                meta=response.meta,
                callback=self.extractCourseUnitInfo)

    def extractCourseUnitInfo(self, response):
        name = response.xpath('//div[@id="conteudoinner"]/h1[2]/text()').extract_first().strip()

        # Checks if the course unit page is valid. 
        # If name == 'Sem Resultados', then it is not.
        if name == 'Sem Resultados':
            return None # Return None as yielding would continue the program and crash at the next assert

        course_unit_id = parse_qs(urlparse(response.url).query)['pv_ocorrencia_id'][0]
        acronym = response.css("#conteudoinner > table:nth-child(4) > tr > td:nth-child(5)::text").extract_first()

        url = response.url
        schedule_url = response.xpath('//a[text()="Horário"]/@href').extract_first()

        # If there is no schedule for this course unit
        if schedule_url is not None:
            schedule_url = response.urljoin(schedule_url)

        course_year = int(response.xpath('//div[@id="conteudoinner"]/table[@class="dados"]//td[@class="l"]/text()').extract_first())

        assert course_year > 0 and course_year < 10

        # Occurrence has a string that contains both the year and the semester type
        occurrence = response.css('#conteudoinner > h2::text').extract_first()

        ## Possible types: '1', '2', 'A', 'SP'
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
              course_unit_id=course_unit_id,
              course_id=response.meta['course_id'],
              name=name,
              acronym=acronym,
              url=url,
              course_year=course_year,
              schedule_url=schedule_url,
              year=year,
              semester=semester,
              last_updated=datetime.now()
        )
