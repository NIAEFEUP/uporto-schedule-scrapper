import getpass
import scrapy
from scrapy.spiders.init import InitSpider
from scrapy.http import Request, FormRequest
from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings


def main():
    user = input("Sigarra login: ")
    password = getpass.getpass("Sigarra password: ")
    crawler = CrawlerProcess({
        "USER_AGENT": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36"
    })
    crawler.crawl(SigarraSpider, user, password)
    crawler.start()


class SigarraSpider(InitSpider):
    name = 'login_feup'
    allowed_domains = ['sigarra.up.pt']
    login_page = 'https://sigarra.up.pt/feup/pt/'
    start_urls = ['https://sigarra.up.pt/feup/pt/vld_validacao.validacao', ]

    def __init__(self, user, password):
        self.user = user
        self.passw = password
        self.inc = 1

    def init_request(self):
        """This function is called before crawling starts."""
        return Request(url=self.login_page, callback=self.login)

    def login(self, response):
        """Generate a login request. The login form needs the following parameters:
            p_app : 162 -> This is always 162
            p_amo : 55 -> This is always 55
            p_address : WEB_PAGE.INICIAL -> This is always 'WEB_PAGE.INICIAL'
            p_user : username -> This is the username used to login
            p_pass : password -> This is the password used to login
        """
        return FormRequest.from_response(response,
                                         formdata={
                                             'p_app': '162', 'p_amo': '55', 'p_address': 'WEB_PAGE.INICIAL', 'p_user': self.user, 'p_pass': self.passw},
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
            print('Sucessfully logged in.')
            # Now the crawling can begin..
            return self.initialized()
            # self.parse(response)
        elif result == "Iniciar sessão":
            # The credentials weren't valid. Try again.
            print('Login failed. Please try again.')
            self.log('Login failed. Please try again.')
        else:
            # Something went wrong, but the result was unexpected.
            # May have been caused by a change in the website structure.
            print('Unexpected result. Website structure may have changed.')
            self.log('Unexpected result. Website structure may have changed.')


# response.xpath('//li/a[contains(@title,"Cursos")]/@href').extract()
    def parse(self, response):
        pag_cursos = response.xpath(
            '//li/a[contains(@title,"Cursos")]/@href').extract_first()
        print('Starting...')
        yield scrapy.Request(url=str(self.login_page) + str(pag_cursos), callback=self.in_curso)
        # Scrape data from page

    def in_curso(self, response):
        print('Entered course page.')
        mest_integrads = response.xpath(
            '//ul[@id="MI_a"]/li/a[1]/@href').extract()

        for mest_intr in mest_integrads:
            yield scrapy.Request(url=str(self.login_page) + str(mest_intr), callback=self.in_mei)

    def in_mei(self, response):
        print('\n\n IN MESTRADO PAGE \n\n')
        horar = response.xpath(
            '//ul/li/a[contains(@title, "Hor")]/@href').extract_first()
        # print('\n\n horario is:' + horar + '\n\n')
        yield scrapy.Request(url=str(self.login_page) + str(horar), callback=self.in_hor)

        # pv_curso_id=742&pv_ano_lectivo=2016&pv_periodos=3
        #<input type="hidden" name="pv_curso_id" value="742">
        #<form action="hor_geral.lista_turmas_curso" method="POST">

    def in_hor(self, response):
        """ Will choose the correct semester and year on the schedules page """
        print('\n\n IN HORARIO PAGE \n\n')
        curso_id = response.xpath(
            '//input[contains(@name, "pv_curso_id")]/@value').extract()
        # print('\n\n CURSO ID '+ curso_id + '\n\n')
        yield FormRequest.from_response(response,
                                        formxpath='//form[contains(@action, "hor_geral.lista_turmas_curso")]',
                                        formdata={
                                            'pv_curso_id': curso_id, 'pv_ano_lectivo': '2016', 'pv_periodos': '3'},
                                        callback=self.in_hor_turm)

    #<input type="hidden" name="pv_turma_id" value="206341">

    def in_hor_turm(self, response):
        if 'tabela' in str(response.body):
            print('\n\n IN THE TABLE THING: WORKED \n\n')
            #turma_ids = response.xpath(
             #   '//input[contains(@name, "pv_turma_id")]/@value').extract()
            #print("\n \n turma ids: " + str(turma_ids))
            #for turma_id in turma_ids:
            self.inc += 1
            self.save_html_file('turma-%s' % str(self.inc), response)
            # go to each class link
            class_links = response.xpath(
                '//table/tr//a/@href').extract()
            for class_link in class_links:
                yield scrapy.Request(url=str(self.login_page) + str(class_link), callback=self.in_class)
        else:
            print('\n\n DAWDAWDAWDSADhor_geral.lista_turmas_curso"W WADASDW \n\n')

    def in_class(self, response):
        self.inc += 1
        print("\n In class Page with schedules \n")
        self.save_html_file("hor_%s" % self.inc, response)

    # mostly for testing porpuses
    def save_html_file(self, name, response):
        filename = '%s.html' % str(name)
        with open(filename, 'wb') as f:
            f.write(response.body)
        self.log('Saved file %s' % filename)


# Used to call main function
if __name__ == "__main__":
    main()
