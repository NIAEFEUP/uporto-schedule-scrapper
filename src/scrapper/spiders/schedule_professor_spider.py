import getpass
import scrapy
from scrapy.http import Request, FormRequest
from urllib.parse import urlencode
from configparser import ConfigParser, ExtendedInterpolation
from dotenv import dotenv_values
import json
from ..database.Database import Database
from ..items import ScheduleProfessor


class ScheduleProfessorSpider(scrapy.Spider):
    name = 'schedule_professor'
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
        super(ScheduleProfessorSpider, self).__init__(*args, **kwargs)
        self.open_config()
        self.user = dotenv_values('.env')['USER']
        self.password = dotenv_values('.env')['PASSWORD']

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
        print("Gathering professors' metadata")
        db = Database() 

        sql = """SELECT url, is_composed, s.professor_sigarra_id as professor_sigarra_id, s.id as schedule_id 
        FROM course_unit c 
        JOIN schedule s ON c.id = s.course_unit_id"""
        db.cursor.execute(sql)
        self.prof_info = db.cursor.fetchall()
        db.connection.close()

        self.log("Crawling {} schedules".format(len(self.prof_info)))

        for (url, is_composed, professor_sigarra_id, schedule_id) in self.prof_info:
            faculty = url.split('/')[3]

            # It is not the sigarra's professor id, but the link to the list of professors. 
            if is_composed:
                yield scrapy.http.Request(
                    url="https://sigarra.up.pt/{}/pt/hor_geral.composto_doc?p_c_doc={}".format(faculty, professor_sigarra_id),
                    meta={'schedule_id': schedule_id},
                    dont_filter=True,
                    callback=self.extractCompoundProfessors)
            else:
            # It is the sigarra's professor id. 
                yield ScheduleProfessor(
                    schedule_id=schedule_id,
                    professor_sigarra_id=professor_sigarra_id,
                )
 
    def extractCompoundProfessors(self, response): 
        professors = response.xpath('//*[@id="conteudoinner"]/li/a/@href').extract()

        for professor_link in professors:
            yield ScheduleProfessor(
                schedule_id=response.meta['schedule_id'],
                professor_sigarra_id=professor_link.split('=')[1],
            )
