import getpass
import scrapy
from scrapy.http import Request, FormRequest
from urllib.parse import urlencode
from configparser import ConfigParser, ExtendedInterpolation
import json
import re 
from ..database.Database import Database
from ..items import CourseUnitYear



class CourseUnitYearSpider(scrapy.Spider):
    name = "course_units_year"
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
        super(CourseUnitYearSpider, self).__init__(*args, **kwargs)
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
                return self.courseRequests()
           

    def courseRequests(self):
        print("Gathering courses")
        db = Database() 

        sql = "SELECT id, url FROM course_unit"
        db.cursor.execute(sql)
        self.course_units = db.cursor.fetchall()
        db.connection.close()

        self.log("Crawling {} courses".format(len(self.course_units)))

        for course_unit in self.course_units:
            yield scrapy.http.Request(
                url=course_unit[1],
                meta={'course_unit_id': course_unit[0]},
                callback=self.extractCourseUnitByYears)

    def extractCourseUnitByYears(self, response): 
        study_cycles = response.xpath('//table[@class="dados"][2]/tr/td').getall()
        i = 0
        study_cycles_len = len(study_cycles)
        course_units = {}

        while (i < study_cycles_len):

            acronym = re.search('>(\D*)<\/a>', study_cycles[i]).group(1)
            course_units[acronym] = []
            num_rows = int(re.search('rowspan="(\d)"', study_cycles[i]).group(1))
            for j in range(7 + num_rows):
                if (j == 3 or j >= 8):
                    course_units[acronym].append(study_cycles[i][study_cycles[i].find('>')+1])
                i+=1

        for (acronym, years) in course_units.items():
            for year in years:
                yield CourseUnitYear(
                        acronym = acronym,    
                        course_unit_id=response.meta['course_unit_id'],
                        course_unit_year=year
                    )
