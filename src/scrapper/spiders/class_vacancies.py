import getpass
import scrapy
from urllib.parse import urlparse, parse_qs
from urllib.parse import urlencode
from configparser import ConfigParser, ExtendedInterpolation
import json

from scrapper.settings import CONFIG, PASSWORD, USERNAME
from ..database.Database import Database
from ..items import Class
from dotenv import dotenv_values
import pandas as pd


class ClassVacancySpider(scrapy.Spider):
    name = "class_vacancies"
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

    def __init__(self, *args, **kwargs):
        super(ClassVacancySpider, self).__init__(*args, **kwargs)
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
            
        yield scrapy.http.Request(url=self.format_login_url(), callback=self.check_login_response, errback=self.login_response_err)

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
                return self.classVancancyRequests()
            
    def classVancancyRequests(self):
        """
        This function is responsible for making the requests to the class vacancies page.
        """
        # Get the list of course units from the database
        db = Database()
        sql = """
            SELECT course.id, year, course.id, faculty.acronym 
            FROM course JOIN faculty 
            ON course.faculty_id= faculty.acronym
        """
        db.cursor.execute(sql)
        self.courses = db.cursor.fetchall()
        self.courses = [22841]
        # Iterate over each course unit and make a request to its class vacancies page
        for course in self.courses:
            url = f"https://sigarra.up.pt/feup/pt/it_geral.vagas?pv_curso_id=22841"
            yield scrapy.Request(
            url=url,
            callback=self.parse_class_vacancies,
            meta={'course': {'id': course}}
        )
                
    def parse_class_vacancies(self, response):
        # Get the table HTML
        table_html = response.css("table.tabela").get()
        
        if not table_html:
            self.logger.error("No table found with class 'tabela'")
            return
        
        try:
            # Read the table
            df = pd.read_html(table_html)[0]
            
            # Print basic info
            print("\nCourse Code | Class Name | Vacancies")
            print("----------------------------------")

            for _, row in df.iterrows():
                course_unit_acronym = row[2]

                i = 0
                while True:
                    if len(row) <= i + 4:
                        break
                    if pd.notna(row[i + 3]) and row[i + 4] != '-':
                        class_name = row[i + 3]
                        vacancy_num = row[i + 4]
                        
                        sql = f"""
                            UPDATE class
                            SET vacancies = ?
                            WHERE course_unit_id = 
                            (SELECT course_unit.id
                            FROM course_unit
                            WHERE course_unit.acronym =  ?
                            AND course_unit.course_id = ?)
                            AND name = ?
                        """
                        db = Database()
                        db.cursor.execute(sql, (vacancy_num, course_unit_acronym, response.meta['course']['id'], class_name))
                    i += 2
                    
        except Exception as e:
            self.logger.error(f"Error processing table: {str(e)}")
            import traceback
            traceback.print_exc()