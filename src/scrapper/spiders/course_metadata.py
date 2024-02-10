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
        self.course_metadatas = set()

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
        print("Gathering courses...")
        db = Database() 

        sql = "SELECT id, sigarra_id FROM course"
        db.cursor.execute(sql)
        self.courses = {sigarra_id: id for id, sigarra_id in db.cursor.fetchall()}

        self.log("Crawling {} courses".format(len(self.courses)))

        print("Gathering course units...")
        sql = "SELECT id, url FROM course_unit"
        db.cursor.execute(sql)
        self.course_units = db.cursor.fetchall()
        db.connection.close()

        self.log("Crawling {} course units".format(len(self.course_units)))

        for course_unit in self.course_units:
            yield scrapy.http.Request(
                url=course_unit[1],
                meta={'course_unit_id': course_unit[0]},
                callback=self.extractCourseUnitByYears)
    
    def extractCourseUnitByYears(self, response): 
        study_cycles = response.xpath('//h3[text()="Ciclos de Estudo/Cursos"]/following-sibling::table[1]').get()
        if study_cycles is None:
            return
        df = pd.read_html(study_cycles, decimal=',', thousands='.')[0]

        for (_, row) in df.iterrows():
            course_unit_id = response.meta['course_unit_id']
            course_acronym = row['Sigla' if 'Sigla' in row else 'Acronym']
            course_url = response.xpath(f'//a[text()="{course_acronym}"]/@href').get()
            if course_url is None:
                continue
            course_sigarra_id = int(course_url.split('=')[1].split('&')[0])
            if course_sigarra_id not in self.courses:
                continue
            course_id = self.courses[course_sigarra_id]
            course_unit_year = row['Anos Curriculares']
            if (course_id, course_unit_id, course_unit_year) in self.course_metadatas:
                continue
            self.course_metadatas.add((course_id, course_unit_id, course_unit_year))
            yield CourseMetadata(
                course_id = course_id,
                course_unit_id = course_unit_id,
                course_unit_year = row['Anos Curriculares'],
                ects = row[5]
            )
