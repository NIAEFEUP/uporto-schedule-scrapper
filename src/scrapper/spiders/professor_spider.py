import getpass
import scrapy
from scrapy.http import Request, FormRequest
from urllib.parse import urlencode
from configparser import ConfigParser, ExtendedInterpolation
import json
from ..database.Database import Database
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

    def __init__(self, category=None, *args, **kwargs):
        super(ProfessorSpider, self).__init__(*args, **kwargs)
        self.open_config()
        self.user = self.config['default']['USER']

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

        sql = "SELECT professor_id FROM schedule"
        db.cursor.execute(sql)
        self.schedules = db.cursor.fetchall()
        db.connection.close()

        self.log("Crawling {} schedules".format(len(self.schedules)))

        for schedule in self.schedules:
            yield scrapy.http.Request(
                url="https://sigarra.up.pt/feup/pt/func_geral.FormView?p_codigo={}".format(schedule[0]),
                meta={'professor_id': schedule[0]},
                callback=self.extractProfessors)

    def extractProfessors(self, response): 
        study_cycles = response.xpath('//h3[text()="Ciclos de Estudo/Cursos"]/following-sibling::table[1]').extract_first()
        acronym = response.xpath("//table[@class='tabelasz']/tbody/tr[2]/td[2]/b").extract_first()
        name = response.xpath("//table[@class='tabelasz']/tbody/tr[1]/td[2]/b").extract_first()
        
        return Professor(
            id = response.meta['professor_id'],
            professor_acronym = acronym,
            professor_name = name
        )
 