import getpass
import scrapy
from datetime import datetime
import urllib.parse
from configparser import ConfigParser, ExtendedInterpolation
import json

from scrapper.settings import CONFIG, PASSWORD, USERNAME

from ..database.Database import Database 
from ..items import Class

class ClassSpider(scrapy.Spider):
    name = "classes"
    allowed_domains = ['sigarra.up.pt']
    login_page_base = 'https://sigarra.up.pt/feup/pt/mob_val_geral.autentica'

    def __init__(self, *args, **kwargs):
        super(ClassSpider, self).__init__(*args, **kwargs)
        self.open_config()
        self.user = CONFIG[USERNAME]
        self.password = CONFIG[PASSWORD]

    def open_config(self):
        """
        Reads and saves the configuration file. 
        """
        config_file = "./config.ini"
        self.config = ConfigParser(interpolation=ExtendedInterpolation())
        self.config.read(config_file) 


    def format_login_url(self):
        return '{}?{}'.format(self.login_page_base, urllib.parse.urlencode({
            'pv_login': self.user,
            'pv_password': self.password
        }))

    def start_requests(self):
        """This function is called before crawling starts."""

        if self.password is None:
            self.password = getpass.getpass(prompt='Password: ', stream=None)

        yield scrapy.http.Request(url=self.format_login_url(), callback=self.check_login_response)

    def check_login_response(self, response):
        """Check the response returned by a login request to see if we are
        successfully logged in. Since we used the mobile login API endpoint,
        we can just check the status code.
        """

        if response.status == 200:
            response_body = json.loads(response.body)
            if response_body['authenticated']:
                self.log("Successfully logged in. Let's start crawling!")
                return self.courseUnitRequests()
            else:
                message = 'Login failed. SIGARRA\'s response: error type "{}";\nerror message "{}"'.format(
                    response_body.erro, response_body.erro_msg)
                print(message, flush=True)
                self.log(message)
        else:
            print('Login Failed. HTTP Error {}'.format(response.status), flush=True)
            self.log('Login Failed. HTTP Error {}'.format(response.status))

    def courseUnitRequests(self):
        db = Database()
        sql = """
            SELECT course_unit.id, course_unit.schedule_url, course.faculty_id
            FROM course_unit JOIN course
            ON course_unit.course_id = course.id
            WHERE schedule_url IS NOT NULL
        """
        db.cursor.execute(sql)
        self.course_units = db.cursor.fetchall()
        db.connection.close()

        self.log("Crawling {} course units to fetch classes".format(len(self.course_units)))
        for course_unit in self.course_units:
            yield scrapy.http.Request(
                url="https://sigarra.up.pt/{}/pt/{}".format(course_unit[2], course_unit[1]),
                meta={'id': course_unit[0], 'faculty': course_unit[2]},
                callback=self.getClassesUrl,
                errback=self.scrapyError
            )

    def getClassesUrl(self, response):
        if response.xpath('//div[@id="erro"]/h2/text()').extract_first() == "Sem Resultados":
            yield None

        classUrl = response.xpath('//span[@class="textopequenoc"]/a/@href').getall()

        for url in classUrl:
            if "turmas_view" in url:
                className = response.xpath('//span[@class="textopequenoc"]/a[@href="'+url+'"]/text()').extract_first()
                yield Class(
                    name=className.strip(),
                    course_unit_id=response.meta['id'],
                    last_updated=datetime.now()
                )
            elif "composto_desc" in url:
                yield scrapy.http.Request(
                    url="https://sigarra.up.pt/{}/pt/{}".format(response.meta['faculty'], url),
                    meta={'id': response.meta['id']},
                    callback=self.extractCompositeClass,
                    errback=self.scrapyError
                )
            else:
                yield None
        
    def extractCompositeClass(self, response):
        classesNames = response.xpath('//div[@id="conteudoinner"]/li/a/text()').getall()
        for className in classesNames:
            yield Class(
                name=className.strip(),
                course_unit_id=response.meta['id'],
                last_updated=datetime.now()
            )

    def scrapyError(self, error):
        # print(error)
        # O Scrapper não tem erros
        return 
