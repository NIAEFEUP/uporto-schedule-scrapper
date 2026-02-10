import getpass
import scrapy
from urllib.parse import urlparse, parse_qs
from urllib.parse import urlencode
from configparser import ConfigParser, ExtendedInterpolation
import json

from scrapper.settings import CONFIG, PASSWORD, USERNAME, VACANCY_COURSES
from ..database.Database import Database
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
        self.allowed_courses = [int(c) for c in CONFIG[VACANCY_COURSES].split(',')]

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
        db = Database()

        sql = """
            SELECT course.id
            FROM course
        """
        db.cursor.execute(sql)
        self.courses = db.cursor.fetchall()
        db.connection.close()


        for course in self.courses:

            course_id = course[0]
            if course_id in self.allowed_courses:
                url = f"https://sigarra.up.pt/feup/pt/it_geral.vagas?pv_curso_id={course_id}"
                yield scrapy.Request(
                url=url,
                callback=self.parse_class_vacancies,
                meta={'course': {'id': course_id}})


    def parse_class_vacancies(self, response):
        db = Database()
        table_html = response.css("table.tabela").get()

        if not table_html:
            self.logger.error("No table found with class 'tabela'")
            return

        try:
            df = pd.read_html(table_html)[0]

            for _, row in df.iterrows():

                course_unit_name = row[1]


                i = 0
                while i + 4 < len(row):

                    if pd.notna(row[i + 3]) and row[i + 4] != '-':
                        class_name = row[i + 3]
                        vacancy_num = row[i + 4]

                        sql = """
                            UPDATE class
                            SET vacancies = ?
                            WHERE course_unit_id =
                            (SELECT course_unit.id
                            FROM course_unit
                            WHERE course_unit.name =  ?
                            AND course_unit.course_id = ?)
                            AND name = ?
                        """
                        db.cursor.execute(sql, (vacancy_num, course_unit_name, response.meta['course']['id'], class_name))
                        db.connection.commit()
                    i += 2

        except Exception as e:
            self.logger.error(f"Error processing table: {str(e)}")
