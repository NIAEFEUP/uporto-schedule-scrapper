import getpass
import scrapy
from scrapy.http import Request, FormRequest
from urllib.parse import urlencode
from configparser import ConfigParser, ExtendedInterpolation
import json

from scrapper.settings import CONFIG, PASSWORD, USERNAME
from ..database.Database import Database
from dotenv import dotenv_values
from ..items import Professor
import pandas as pd


class ProfessorSpider(scrapy.Spider):
    name = "professors"
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
        super(ProfessorSpider, self).__init__(*args, **kwargs)
        self.open_config()
        self.user = CONFIG[USERNAME]
        self.password = CONFIG[PASSWORD]

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
                return self.scheduleRequests()
           

    def scheduleRequests(self):
        print("Gathering professors")
        db = Database() 
        
        sql = """
        SELECT slot_professor.professor_id, url 
        FROM course_unit JOIN class JOIN slot JOIN slot_professor
        ON course_unit.id = class.course_unit_id AND class.id = slot.class_id AND slot.id = slot_professor.slot_id
        GROUP BY slot_professor.professor_id
        """
        db.cursor.execute(sql)
        self.prof_info = db.cursor.fetchall()
        db.connection.close()

        self.log("Crawling {} schedules".format(len(self.prof_info)))


        for (id, url) in self.prof_info:
            faculty = url.split('/')[3]
            yield scrapy.http.Request(
                url="https://sigarra.up.pt/{}/pt/func_geral.FormView?p_codigo={}".format(faculty, id),
                meta={'professor_id': id},
                callback=self.extractProfessors)

    def extractProfessors(self, response): 
        name = response.xpath('//table[@class="tabelasz"]/tr[1]/td[2]/b/text()').extract_first()
        acronym = response.xpath('//table[@class="tabelasz"]/tr[2]/td[2]/b/text()').extract_first()
        return Professor(
            id = response.meta['professor_id'],
            professor_acronym = acronym,
            professor_name = name
        )
 
