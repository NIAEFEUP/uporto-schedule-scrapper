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
        "USER_AGENT": "NIAFEUP (ni@aefeup.pt)"
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
            #turma_id = response.xpath(
             #   '//input[contains(@name, "pv_turma_id")]/@value').extract()
            self.inc += 1
            self.save_html_file('turma-%s' % str(self.inc), response)
            # go to each class link
            class_links = response.xpath(
                '//table/tr//a/@href').extract()
            for class_link in class_links:
                yield scrapy.Request(url=str(self.login_page) + str(class_link), callback=self.in_class)
        else:
            print('\n\n ERROR occured while gettin each class url. Continuing.\n\n')

    def in_class(self, response):
        self.inc += 1
        print("\n In class Page with schedules \n")
        self.save_html_file("hor_%s" % self.inc, response)

    # mostly for testing porpuses
    def save_html_file(self, name, response, ext = 'html'):
        filename = '%s.%s' % (str(name), ext)
        with open(filename, 'wb') as f:
            f.write(response.body)
        self.log('Saved file %s' % filename)
        info_curso_name = response.xpath('//div[@id="barralocalizacao"]/a/@title').extract()[1]
        info_all_classes = response.xpath('//table[@class="horario"]/tr/td[@rowspan>"0"]/..')
    """
        a class ex : info_all_classes[0]
        following apply to a single class:
            time start (ex: 8.30 - 9.30)  -> xpath('td[@class="horas k"]/text()').extract()
            duration (nº of 30m blocks)   -> xpath('td[@rowspan]/@rowspan').extract()
            type (ex: TP, TE)             -> xpath('td[@rowspan]/@class').extract()
            title (ex: Programaçao)       -> xpath('td[@rowspan]/b/acronym/@title').extract()
            title acronym (ex: Prog)      -> xpath('td[@rowspan]/b//a/text()').extract()
            title url                     -> xpath('td[@rowspan]/b//a/@href').extract()
            location (ex: B005)           -> xpath('td/table//a/text()').extract()
            professor (ex: Jorge Silva)   -> xpath('//td[@class = "textod"]//@title').extract()
            professor acronym (ex: JAS)   -> xpath('//td[@class = "textod"]//a/text()').extract()
            professor url                 -> xpath('//td[@class = "textod"]//a/@href').extract()
            class id (ex: COMP 1253)      -> xpath('//span[@class = "textopequenoc"]/a/text()').extract()
            week day   (WIP)              -> response.xpath('//table[@class="horario"]/tr//td[@class="horas" or @class = "horas k"]').extract()
    """

# Used to call main function
if __name__ == "__main__":
    main()


"""
response.xpath('//table[@class="horario"]/tr//td[@class="horas" or @class = "horas k"]/..').extract()
response.xpath('//table[@class="horario"]/tr//td[@class="horas" or @class = "horas k"]/..')[12]
hor_21.html
"""