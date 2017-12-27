import scrapy
import getpass
from ..items import Class
from scrapy.http import Request, FormRequest
from ..con_info import ConInfo

class CourseUnitSpider(scrapy.Spider):
    name = "courseUnits"
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
        return FormRequest.from_response(response,
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
        # print(self.courses)
        # return
        for course in self.courses:
            # print({'pv_curso_id': str(course[2]), 'pv_ano_lectivo': str(course[1]), 'pv_periodos': str(1)})
            yield scrapy.http.Request(
                url='https://sigarra.up.pt/{}/pt/ucurr_geral.pesquisa_ocorr_ucs_list?pv_ano_lectivo={}&pv_curso_id={}'.format(course[3], course[1], course[2]),
                meta={'course_id': course[0]},
                callback=self.extractCourseUnits)
    
    def extractCourseUnits(self, response):
        print(response.css("#conteudoinner > div > div.paginar-paginas > div > div.paginar-paginas-posteriores > span:last-child > a"))

            
           
