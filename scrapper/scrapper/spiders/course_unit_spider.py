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
        self.passw = getpass.getpass(prompt='Password: ', stream=None)
        yield FormRequest.from_response(response,
                                        formdata={
                                            'p_app': '162', 'p_amo': '55',
                                            'p_address': 'WEB_PAGE.INICIAL',
                                            'p_user': self.user,
                                            'p_pass': self.passw},
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
        course_unit_id = parse_qs(urlparse(response.url).query)['pv_ocorrencia_id'][0]
        name = response.css("#conteudoinner > h1:nth-child(3)::text").extract_first()
        acronym = response.css("#conteudoinner > table:nth-child(4) > tr > td:nth-child(5)::text").extract_first()
        url = response.url
        schedule_url = response.xpath('//a[text()="Horário"]/@href').extract_first()

        # If there is no schedule for this course unit
        if schedule_url is not None:
            schedule_url = response.urljoin(schedule_url)

        yield CourseUnit(
            course_unit_id=course_unit_id,
            course_id=response.meta['course_id'],
            name=name,
            acronym=acronym,
            url=url,
            schedule_url=schedule_url,
            last_updated=datetime.now()
        )
