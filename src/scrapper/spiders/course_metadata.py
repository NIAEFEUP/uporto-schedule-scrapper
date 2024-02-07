import getpass
import scrapy
from scrapy.http import Request, FormRequest
from urllib.parse import urlencode
from configparser import ConfigParser, ExtendedInterpolation
import json

from scrapper.settings import CONFIG, PASSWORD, USERNAME
from ..database.Database import Database
from ..items import CourseMetadata
from dotenv import dotenv_values
import pandas as pd


class CourseMetadataSpider(scrapy.Spider):
    name = "course_metadata"
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
        super(CourseMetadataSpider, self).__init__(*args, **kwargs)
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
                return self.courseRequests()
           

    def courseRequests(self):
        print("Gathering course metadata...")
        db = Database() 

        sql = "SELECT cu.id, cu.url, cu.course_id, c.sigarra_id FROM course_unit cu JOIN course c ON c.id=cu.course_id"
        db.cursor.execute(sql)
        self.course_units = db.cursor.fetchall()
        db.connection.close()

        self.log("Crawling {} courses".format(len(self.course_units)))

        for course_unit in self.course_units:
            yield scrapy.http.Request(
                url=course_unit[1],
                meta={'course_unit_id': course_unit[0], 'course_unit_sigarra_id': course_unit[3]},
                callback=self.extractCourseUnitByYears)
    
    def extractCourseUnitByYears(self, response): 
        study_cycles = response.xpath('//h3[text()="Ciclos de Estudo/Cursos"]/following-sibling::table[1]').get()
        df = pd.read_html(study_cycles, decimal=',', thousands='.')[0]

        for (_, row) in df.iterrows():
            yield CourseMetadata(
                course_id = response.meta['course_id'],
                course_unit_id = response.meta['course_unit_id'],
                course_unit_year = row['Anos Curriculares'],
                ects = row[5]
            )
