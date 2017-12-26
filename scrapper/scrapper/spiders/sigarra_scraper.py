import scrapy
from scrapy.spiders.init import InitSpider
from scrapy.http import Request, FormRequest
from ..items import Schedule


class SigarraSpider(InitSpider):
    name = 'login_feup'
    allowed_domains = ['sigarra.up.pt']
    login_page = 'https://sigarra.up.pt/feup/pt/'
    start_urls = ['https://sigarra.up.pt/feup/pt/vld_validacao.validacao', ]

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
            return self.initialized()
        elif result == "Iniciar sessão":
            print('Login failed. Please try again.')
            self.log('Login failed. Please try again.')
        else:
            print('Unexpected result. Website structure may have changed.')
            self.log('Unexpected result. Website structure may have changed.')

    def parse(self, response):
        """
        Hook method for the spider, called for each request and will
        generate further requests
        """
        pag_cursos = response.xpath(
            '//li/a[contains(@title,"Cursos")]/@href').extract_first()
        print('Starting...')
        yield scrapy.Request(url=str(self.login_page) + str(pag_cursos),
                             callback=self.in_curso)

    def in_curso(self, response):
        print('Entered course page.')
        mest_integrads = response.xpath(
            '//ul[@id="MI_a"]/li/a[1]/@href').extract()

        for mest_intr in mest_integrads:
            yield scrapy.Request(url=str(self.login_page) + str(mest_intr),
                                 callback=self.in_mei)

    def in_mei(self, response):
        print('\n\n IN MESTRADO PAGE \n\n')
        horar = response.xpath(
            '//ul/li/a[contains(@title, "Hor")]/@href').extract_first()
        yield scrapy.Request(url=str(self.login_page) + str(horar),
                             callback=self.in_hor)

    def in_hor(self, response):
        """ Will choose the correct semester and year on the schedules page """
        print('\n\n IN HORARIO PAGE \n\n')
        curso_id = response.xpath(
            '//input[contains(@name, "pv_curso_id")]/@value').extract()
        yield FormRequest.from_response(response,
            formxpath='//form[contains(@action, "hor_geral.lista_turmas_curso")]',
            formdata={
                'pv_curso_id': curso_id, 'pv_ano_lectivo': '2016',
                'pv_periodos': '3'},
            callback=self.in_hor_turm)

    def in_hor_turm(self, response):
        if 'tabela' in str(response.body):
            class_links = response.xpath(
                '//table/tr//a/@href').extract()
            for class_link in class_links:
                yield scrapy.Request(url=str(self.login_page) + str(class_link), callback=self.in_class)
        else:
            print('\nERROR occured while gettin each class url. Continuing.\n')

    def in_class(self, response):
        info_curso_name = response.xpath('//div[@id="barralocalizacao"]/a/@title').extract()[1]
        info_all_classes = response.xpath('//table[@class="horario"]/tr/td[@rowspan>"0"]/..')
        class_id = response.xpath('//h1/text()').extract_first().split(' ')[-1]

        for block in info_all_classes: # a block is a 30m period, only shows the classes that start.
            info_title = block.xpath('td[@rowspan]/b/acronym/@title').extract()
            info_text = block.xpath('td[@rowspan]/span[@class = "textopequenoc"]/a/text()').extract()
            info_type = block.xpath('td[@rowspan]/@class').extract()
            info_date = block.xpath('td[@class="horas k"]/text()').extract()
            info_duration = block.xpath('td[@rowspan]/@rowspan').extract()
            info_classacro = block.xpath('td[@rowspan]/b//a/text()').extract()
            info_proff_full = block.xpath('td[@rowspan]//td[@class="textod"]//acronym/@title | td[@rowspan]//td[@class="textod"][not(acronym)]').extract()
            info_proff_acronym = block.xpath('td[@rowspan]//td[@class="textod"]//a/text()').extract()
            info_class_acronym = block.xpath('td[@rowspan]/span[@class = "textopequenoc"]/a/text()').extract()
            info_class_loc = block.xpath('td/table//a/text()').extract()[0::2]

        for i in range(len(info_title)):
            #the informations arrays might have different, especeally when a class has more than 1 professor (ex: TP: JMC+LPE)
            sch_item = Schedule()
            sch_item['course'] = info_curso_name[i]
            sch_item['date'] = info_date[0]
            sch_item['title'] = info_type[i]
            sch_item['text'] = info_text[i]
            sch_item['duration'] = info_duration[i]
            sch_item['acronym'] = info_classacro[i]
            sch_item['professor'] = info_proff_full[i]
            sch_item['prof_acro'] = info_proff_acronym[i]
            sch_item['id_class'] = info_class_acronym[i]
            sch_item['location'] = info_class_loc[i]
            yield sch_item
