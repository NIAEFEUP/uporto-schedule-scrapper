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
from ..items import Slot, Class, SlotProfessor, Professor, SlotClass


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

    if (class_id == None):  # TODO: verificar casos em que a aula já esta na db mas for some reason não foi encontrada
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
        self.professor_name_pattern = "\d+\s-\s[A-zÀ-ú](\s[A-zÀ-ú])*"
        self.inserted_teacher_ids = set()

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
            print('Login Failed. HTTP Error {}'.format(
                response.status), flush=True)
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
            course_unit_id = course_unit[0]
            # e.g. hor_geral.ucurr_view?pv_ocorrencia_id=514985
            link_id_fragment = course_unit[1]
            faculty = course_unit[2]

            yield Request(
                url="https://sigarra.up.pt/{}/pt/{}".format(
                    faculty, link_id_fragment),
                meta={'course_unit_id': course_unit_id},
                callback=self.makeRequestToSigarraScheduleAPI,
                errback=self.func
            )

    def func(self, error):
        # # O scrapper não tem erros
        print("An error has occured: ", error)
        return

    def makeRequestToSigarraScheduleAPI(self, response):
        self.api_url = response.xpath(
            '//div[@id="cal-shadow-container"]/@data-evt-source-url').extract_first()

        yield Request(url=self.api_url, callback=self.extractSchedule, meta={'course_unit_id': re.search(r'uc/(\d+)/', self.api_url).group(1)})

    def extractSchedule(self, response):
        schedule_data = response.json()["data"]
        course_unit_id = response.meta.get('course_unit_id')

        if len(schedule_data) < 1:
            return

        date_format = "%Y-%m-%dT%H:%M:%S"

        inserted_slots_ids = []
        for schedule in schedule_data:
            if (schedule['id'] in inserted_slots_ids):
                continue
            inserted_slots_ids.append(schedule['id'])

            start_time = datetime.strptime(schedule["start"], date_format)
            end_time = datetime.strptime(schedule["end"], date_format)

            for teacher in schedule["persons"]:
                (sigarra_id, name) = self.get_professor_info(teacher)

                if sigarra_id in self.inserted_teacher_ids:
                    continue

                self.inserted_teacher_ids.add(sigarra_id)

                yield Professor(
                    id=sigarra_id,
                    professor_acronym=teacher["acronym"],
                    professor_name=name
                )

            for current_class in schedule["classes"]:
                yield Class(
                    name=current_class["name"],
                    course_unit_id=course_unit_id,
                    last_updated=datetime.now()
                )

                yield Slot(
                    id=schedule["id"],
                    lesson_type=schedule["typology"]["acronym"],
                    day=self.days[schedule["week_days"][0]],
                    start_time=start_time.hour + (start_time.minute / 60),
                    duration=(end_time - start_time).total_seconds() / 3600,
                    location=schedule["rooms"][0]["name"],
                    is_composed=len(schedule["classes"]) > 0,
                    professor_id=schedule["persons"][0]["sigarra_id"],
                    last_updated=datetime.now()
                )

                for teacher in schedule["persons"]:
                    (sigarra_id, name) = self.get_professor_info(
                        teacher)

                    yield SlotProfessor(
                        slot_id=schedule["id"],
                        professor_id=sigarra_id
                    )

            for current_class in schedule["classes"]:
                yield SlotClass(
                    slot_id=schedule["id"],
                    class_id=get_class_id(
                        course_unit_id, current_class["name"])
                )

                

    def get_professor_info(self, teacher):
        """
            The sigarra API that are using gives the name of the professors in two ways:
            1. <sigarra_code> - <professor_name>
            2. <name>

            The option 2 generally occurs when there is not any teacher assigned. So, in order to retrive the
            <professor_name> in the cases that we have a '-' in the middle, we have to check which one of option 1
            or option 2 the api returned for that specific class.
        """

        if re.search(self.professor_name_pattern, teacher["name"]):
            [professor_sigarra_id, professor_name,
                *_] = teacher["name"].split("-", 1)

            return (professor_sigarra_id.strip(), professor_name.strip())

        return (teacher["sigarra_id"], teacher["name"])
