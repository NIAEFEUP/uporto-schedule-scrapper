import getpass
import re
import scrapy
from datetime import datetime
from scrapy.http import Request, FormRequest
import urllib.parse
from configparser import ConfigParser, ExtendedInterpolation
import json
from datetime import time

from scrapper.settings import CONFIG, PASSWORD, USERNAME

from ..database.Database import Database 
from ..items import Slot, Class, SlotProfessor, Professor

def get_class_id(course_unit_id, class_name):
    db = Database()
    sql = """
        SELECT class.id, course_unit.url
        FROM course_unit JOIN class 
        ON course_unit.id = class.course_unit_id 
        WHERE course_unit.id = {} AND class.name = '{}'
    """.format(course_unit_id, class_name)
    
    db.cursor.execute(sql)
    class_id = db.cursor.fetchone()
    db.connection.close()

    if (class_id == None): # TODO: verificar casos em que a aula já esta na db mas for some reason não foi encontrada
        # db2 = Database()
        # sql = """
        #     SELECT course_unit.url
        #     FROM course_unit  
        #     WHERE course_unit.id = {}
        # """.format(course_unit_id)

        # db2.cursor.execute(sql)
        # class_url = db2.cursor.fetchone()
        # db2.connection.close()
        # print("Class not found: ", class_url[0])
        return None    
    return class_id[0]

class SlotSpider(scrapy.Spider):
    name = "slots"
    allowed_domains = ['sigarra.up.pt']
    login_page_base = 'https://sigarra.up.pt/feup/pt/mob_val_geral.autentica'
    days = {'Segunda-feira': 0, 'Terça-feira': 1, 'Quarta-feira': 2,
            'Quinta-feira': 3, 'Sexta-feira': 4, 'Sábado': 5}

    def __init__(self, password=None, category=None, *args, **kwargs):
        super(SlotSpider, self).__init__(*args, **kwargs)
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

        yield Request(url=self.format_login_url(), callback=self.check_login_response)

    def check_login_response(self, response):
        """Check the response returned by a login request to see if we are
        successfully logged in. Since we used the mobile login API endpoint,
        we can just check the status code.
        """

        if response.status == 200:
            response_body = json.loads(response.body)
            if response_body['authenticated']:
                self.log("Successfully logged in. Let's start crawling!")
                return self.classUnitRequests()
            else:
                message = 'Login failed. SIGARRA\'s response: error type "{}";\nerror message "{}"'.format(
                    response_body.erro, response_body.erro_msg)
                print(message, flush=True)
                self.log(message)
        else:
            print('Login Failed. HTTP Error {}'.format(response.status), flush=True)
            self.log('Login Failed. HTTP Error {}'.format(response.status))

    def classUnitRequests(self):
        db = Database()        
        sql = """
            SELECT course_unit.id, course_unit.schedule_url, course.faculty_id
            FROM course JOIN course_metadata JOIN course_unit
            ON course.id = course_metadata.course_id AND course_metadata.course_unit_id = course_unit.id
            WHERE schedule_url IS NOT NULL
        """
        db.cursor.execute(sql)
        self.course_units = db.cursor.fetchall()
        db.connection.close()

        self.log("Crawling {} class units".format(len(self.course_units)))
        for course_unit in self.course_units:
            yield Request(                
                url="https://sigarra.up.pt/{}/pt/{}".format(course_unit[2], course_unit[1]),
                meta={'course_unit_id': course_unit[0]},
                callback=self.makeRequestToSigarraScheduleAPI,
                errback=self.func
            )
            
    def func(self, error):
        # # O scrapper não tem erros
        # print(error)
        return

    def makeRequestToSigarraScheduleAPI(self, response):
        self.api_url = response.xpath('//div[@id="cal-shadow-container"]/@data-evt-source-url').extract_first()

        yield Request(url=self.api_url, callback=self.extractSchedule)

    def extractSchedule(self, response):
        schedule_data = response.json()["data"]
        slot_ids = set()

        for schedule in schedule_data:
            date_format = "%Y-%m-%dT%H:%M:%S"
            start_time = datetime.strptime(schedule["start"], date_format)
            end_time = datetime.strptime(schedule["end"], date_format)

            if(int(schedule["id"]) in slot_ids):
                continue

            slot_ids.add(int(schedule["id"]))

            yield Class(
                id=schedule["id"],
                name=schedule["name"],
                course_unit_id=re.search(r'uc/(\d+)/', self.api_url).group(1),
                last_updated=datetime.now()
            )

            yield Slot(
                id=schedule["id"],
                lesson_type=schedule["typology"]["acronym"],
                day=self.days[schedule["week_days"][0]],
                start_time=start_time.hour + (start_time.minute / 60),
                duration=(end_time - start_time).total_seconds() / 3600,
                location=schedule["rooms"][0]["name"],
                is_composed=len(schedule["persons"]) > 0,
                professor_id=schedule["persons"][0]["sigarra_id"],
                class_id=schedule["id"],
                last_updated=datetime.now(),
            )
            
            for teacher in schedule["persons"]:
                yield Professor(
                    id = teacher["sigarra_id"],
                    professor_acronym = teacher["acronym"],
                    professor_name = teacher["name"].split("-")[1].strip()
                )

                yield SlotProfessor(
                    slot_id=schedule["id"],
                    professor_id=teacher["sigarra_id"]
                )
