import scrapy
from scrapy.contrib.spiders.init import InitSpider
from scrapy.http import Request, FormRequest
from scrapy.linkextractors import LinkExtractor
from scrapy.contrib.spiders import Rule

class MySpider(InitSpider):
    name = 'login_feup'
    allowed_domains = ['sigarra.up.pt']
    login_page = 'https://sigarra.up.pt/feup/pt/'
    start_urls = ['https://sigarra.up.pt/feup/pt/vld_validacao.validacao', ]

    #rules = (
    #    Rule(SgmlLinkExtractor(allow=r'-\w+.html$'),
    #         callback='parse_item', follow=True),
    #)

    def __init__(self, user, password):
        self.user = user
        self.passw = password

    def init_request(self):
        """This function is called before crawling starts."""
        return Request(url=self.login_page, callback=self.login)

#p_app=162&p_amo=55&p_address=WEB_PAGE.INICIAL&p_user=ouser&p_pass=asenha

    def login(self, response):
        """Generate a login request."""
        return FormRequest.from_response(response,
                    formdata={'p_app': '162', 'p_amo': '55', 'p_address':'WEB_PAGE.INICIAL', 'p_user':self.user, 'p_pass':self.passw},
                    callback=self.check_login_response)

    def check_login_response(self, response):
        """Check the response returned by a login request to see if we are
        successfully logged in.
        """
        if "Vasconcelos" in str(response.body):
            self.log("Successfully logged in. Let's start crawling!")
            print('\n\nSucessfully logged in\n\n')
            # Now the crawling can begin..
            return self.initialized()
            #self.parse(response)
        else:
            print('\n\n COULDNT LOGIN \n\n')
            self.log("Bad times :(")
            # Something went wrong, we couldn't log in, so nothing happens.
            

#response.xpath('//li/a[contains(@title,"Cursos")]/@href').extract()
    def parse(self, response):
        pag_cursos = response.xpath('//li/a[contains(@title,"Cursos")]/@href').extract_first()
        print('\n\n HELLO IN PARGE PAGE \n\n')
        yield scrapy.Request(url=str(self.login_page) + str(pag_cursos), callback=self.in_curso)
        # Scrape data from page

    def in_curso(self, response):
        print('IN PAGINA DO CURSOS')
        mest_integrads = response.xpath('//ul[@id="MI_a"]//a/@href').extract()
        for mest_intr in mest_integrads:
            yield scrapy.Request(url=str(self.login_page) + str(mest_intr), callback=self.in_mei)

    def in_mei(self, response):
        print('\n\n IN MESTRADO PAGE \n\n')
        horar = response.xpath('//ul/li/a[contains(@title, "Hor")]/@href').extract_first()
        #print('\n\n horario is:' + horar + '\n\n')
        yield scrapy.Request(url=str(self.login_page) + str(horar), callback=self.in_hor)

        #pv_curso_id=742&pv_ano_lectivo=2016&pv_periodos=3
        #<input type="hidden" name="pv_curso_id" value="742">
        #<form action="hor_geral.lista_turmas_curso" method="POST">

    def in_hor(self, response):
        print('\n\n IN HORARIO PAGE \n\n')
        curso_id = response.xpath('//input[contains(@name, "pv_curso_id")]/@value').extract_first()
        #print('\n\n CURSO ID '+ curso_id + '\n\n')
        yield FormRequest.from_response(response,
                    formxpath='//form[contains(@action, "hor_geral.lista_turmas_curso")]',
                    formdata={'pv_curso_id': curso_id, 'pv_ano_lectivo':'2016', 'pv_periodos':'3'},
                    callback=self.in_hor_turm)

    #<input type="hidden" name="pv_turma_id" value="206341">

    def in_hor_turm(self, response):
        if 'tabela' in str(response.body):
            print('\n\n IN THE TABLE THING: WORKED \n\n')
            turma_id = response.xpath('//input[contains(@name, "pv_turma_id")]/@value').extract_first()
        else:
            print('\n\n DAWDAWDAWDSADhor_geral.lista_turmas_curso"W WADASDW \n\n')
