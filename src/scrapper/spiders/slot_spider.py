import getpass
import scrapy
from datetime import datetime
from scrapy.http import Request, FormRequest
import urllib.parse
from configparser import ConfigParser, ExtendedInterpolation
import json

from scrapper.settings import CONFIG, PASSWORD, USERNAME

from ..database.Database import Database 
from ..items import Slot

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
    days = {'Segunda': 0, 'Terça': 1, 'Quarta': 2,
            'Quinta': 3, 'Sexta': 4, 'Sábado': 5}
    scraped_slots = set()
    # password = None

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
                meta={'course_unit_id': course_unit[0], 'faculty': course_unit[2], 'schedule_url': course_unit[1]},
                callback=self.getScheduleBlocks,
                errback=self.func
            )
            
    def func(self, error):
        # # O scrapper não tem erros
        # print(error)
        return
    
    def getScheduleBlocks(self, response):
        if response.xpath('//div[@id="erro"]/h2/text()').extract_first() == "Sem Resultados":
            yield None

        week_blocks = list(set(
            response.xpath('//td[@class="l sem-quebra"]//a/@href').getall() 
                               + 
            response.xpath('//td[@class="bloco-select sem-quebra"]//a/@href').getall()
           ))
        
        if (len(week_blocks) == 0):
            yield scrapy.http.Request(
                url="https://sigarra.up.pt/{}/pt/{}".format(response.meta['faculty'], response.meta['schedule_url']),
                meta=response.meta,
                callback=self.extractSchedule,
                errback=self.func
            )
        else:
            for week_block in week_blocks:
                yield scrapy.http.Request(
                    url="https://sigarra.up.pt/{}/pt/{}".format(response.meta['faculty'], week_block),
                    meta=response.meta,
                    callback=self.extractSchedule,
                    errback=self.func
                )
    
    def extractSchedule(self, response):
        # Classes in timetable
        for schedule in response.xpath('//table[@class="horario"]'):
            # This array represents the rowspans left in the current row
            # It is used because when a row has rowspan > 1, the table
            # will seem to be missing a column and can cause out of sync errors
            # between the HTML table and its memory representation
            rowspans = [0, 0, 0, 0, 0, 0]
            hour = 8
            for row in schedule.xpath('./tr[not(th)]'):
                cols = row.xpath('./td[not(contains(@class, "k"))]')
                cols_iter = iter(cols)

                # 0 -> Monday, 1 -> Tuesday, ..., 5 -> Saturday (No sunday)
                for cur_day in range(0, 6):
                    if rowspans[cur_day] > 0:
                        rowspans[cur_day] -= 1

                    # If there is a class in the current column, then just
                    # skip it
                    if rowspans[cur_day] > 0:
                        continue

                    cur_col = next(cols_iter)
                    class_duration = cur_col.xpath('@rowspan').extract_first()
                    if class_duration is not None:
                        rowspans[cur_day] = int(class_duration)
                        yield self.extractClassSchedule(
                            response, 
                            cur_col, 
                            cur_day, 
                            hour, 
                            int(class_duration) / 2,
                            response.meta['course_unit_id']
                        )

                hour += 0.5

        # Overlapping classes
        for row in response.xpath('//table[@class="dados"]/tr[not(th)]'):
            yield self.extractOverlappingClassSchedule(response, row, response.meta['course_unit_id'])

    def extractClassSchedule(self, response, cell, day, start_time, duration, course_unit_id):

        lesson_type = cell.xpath(
            'b/text()').extract_first().strip().replace('(', '', 1).replace(')', '', 1)
        table = cell.xpath('table/tr')
        location = table.xpath('td/a/text()').extract_first()
        professor_link = table.xpath('td[@class="textod"]//a/@href').extract_first()
        is_composed = 'composto_doc' in professor_link
        professor_id = professor_link.split('=')[1]

        clazz = cell.xpath('span/a')
        class_name = clazz.xpath('text()').extract_first()
        class_url = clazz.xpath('@href').extract_first()

        # If true, this means the class is composed of more than one class
        # And an additional request must be made to obtain all classes
        if "hor_geral.composto_desc" in class_url:
            return response.follow(
                class_url,
                dont_filter=True,
                meta={
                    'course_unit_id': course_unit_id, 
                    'lesson_type': lesson_type, 
                    'start_time': start_time, 
                    'is_composed': is_composed,
                    'professor_id': professor_id, 
                    'location': location, 
                    'day': day,
                    'duration': duration
                },
                callback=self.extractComposedClasses
            )

        class_id = get_class_id(course_unit_id, class_name)
        if (class_id != None):

            slot_identifier = (course_unit_id, lesson_type, day, start_time, duration, location, is_composed, professor_id, class_id)

            if slot_identifier in self.scraped_slots:
                return None 
            else:
                self.scraped_slots.add(slot_identifier)

            return Slot(
                lesson_type=lesson_type,
                day=day,
                start_time=start_time,
                duration=duration,
                location=location,
                is_composed=is_composed,
                professor_id=professor_id,
                class_id=class_id,
                last_updated=datetime.now(),
            )
        else: 
            return None 

    def extractComposedClasses(self, response):
        class_names = response.xpath(
            '//div[@id="conteudoinner"]/li/a/text()').extract()

        for class_name in class_names:
            class_id = get_class_id(response.meta['course_unit_id'], class_name)
            if (class_id != None):

                slot_identifier = (response.meta['course_unit_id'], response.meta['lesson_type'], response.meta['day'], response.meta['start_time'], response.meta['duration'], response.meta['location'], response.meta['is_composed'], response.meta['professor_id'], class_id)
                
                if slot_identifier in self.scraped_slots:
                    return None
                else:
                    self.scraped_slots.add(slot_identifier)
                yield Slot(
                        lesson_type=response.meta['lesson_type'],
                        day=response.meta['day'],
                        start_time=response.meta['start_time'],
                        duration=response.meta['duration'],
                        location=response.meta['location'],
                        is_composed=response.meta['is_composed'],
                        professor_id=response.meta['professor_id'],
                        class_id=class_id,
                        last_updated=datetime.now()
                    )
            else:
                yield None

    def extractOverlappingClassSchedule(self, response, row, course_unit_id):
        day_str = row.xpath('td[2]/text()').extract_first()
        time_str = row.xpath('td[3]/text()').extract_first()

        day = self.days[day_str]
        hours, minutes = time_str.split(':')
        start_time = int(hours)

        if int(minutes) > 0:
            start_time += int(minutes) / 60

        lesson_type = row.xpath(
            'td[1]/text()').extract_first().strip().replace('(', '', 1).replace(')', '', 1)
        location = row.xpath('td[4]/a/text()').extract_first()
        professor_link = row.xpath('td[@headers="t5"]/a/@href').extract_first()
        is_composed = 'composto_doc' in professor_link
        professor_id = professor_link.split('=')[1]

        clazz = row.xpath('td[6]/a')
        class_name = clazz.xpath('text()').extract_first()
        class_url = clazz.xpath('@href').extract_first()

        # If true, this means the class is composed of more than one class
        # And an additional request must be made to obtain all classes
        if "hor_geral.composto_desc" in class_url:
            return response.follow(
                class_url,
                dont_filter=True,
                meta={
                    'course_unit_id': course_unit_id, 
                    'lesson_type': lesson_type, 
                    'start_time': start_time, 
                    'is_composed': is_composed,
                    'professor_id': professor_id, 
                    'location': location, 
                    'day': day
                    },
                callback=self.extractDurationFromComposedOverlappingClasses
            )

        return response.follow(
            class_url,
            dont_filter=True,
            meta={
                'course_unit_id': course_unit_id, 
                'lesson_type': lesson_type, 
                'start_time': start_time, 
                'is_composed': is_composed,
                'professor_id': professor_id, 
                'location': location, 
                'day': day,
                'class_name': class_name
            },
            callback=self.extractDurationFromOverlappingClass
        )

    def extractDurationFromComposedOverlappingClasses(self, response):
        classes = response.xpath('//div[@id="conteudoinner"]/li/a')

        for clazz in classes:
            class_name = clazz.xpath('./text()').extract_first()
            class_url = clazz.xpath('@href').extract_first()

            yield response.follow(
                class_url,
                dont_filter=True,
                meta={
                    'course_unit_id': response.meta['course_unit_id'], 
                    'lesson_type': response.meta['lesson_type'], 
                    'start_time': response.meta['start_time'],
                    'is_composed': response.meta['is_composed'], 
                    'professor_id': response.meta['professor_id'],
                    'location': response.meta['location'], 
                    'day': response.meta['day'],
                    'class_name': class_name
                },
                callback=self.extractDurationFromOverlappingClass
            )

    def extractDurationFromOverlappingClass(self, response):
        day = response.meta['day']
        start_time = response.meta['start_time']
        duration = None

        # Classes in timetable
        for schedule in response.xpath('//table[@class="horario"]'):
            # This array represents the rowspans left in the current row
            # It is used because when a row has rowspan > 1, the table
            # will seem to be missing a column and can cause out of sync errors
            # between the HTML table and its memory representation
            rowspans = [0, 0, 0, 0, 0, 0]
            hour = 8
            for row in schedule.xpath('./tr[not(th)]'):
                cols = row.xpath('./td[not(contains(@class, "k"))]')
                cols_iter = iter(cols)

                # 0 -> Monday, 1 -> Tuesday, ..., 5 -> Saturday (No sunday)
                for cur_day in range(0, 6):
                    if rowspans[cur_day] > 0:
                        rowspans[cur_day] -= 1

                    # If there is a class in the current column, then just
                    # skip it
                    if rowspans[cur_day] > 0:
                        continue

                    cur_col = next(cols_iter)
                    class_duration = cur_col.xpath('@rowspan').extract_first()
                    if class_duration is not None:
                        rowspans[cur_day] = int(class_duration)
                        if cur_day == day and start_time == hour:
                            duration = int(class_duration) / 2

                hour += 0.5

        if duration is None:
            return None
        

        

        class_id = get_class_id(response.meta['course_unit_id'], response.meta['class_name'])
        if (class_id != None):
            slot_identifier = (response.meta['course_unit_id'], response.meta['lesson_type'], day, start_time, duration, response.meta['location'], response.meta['is_composed'], response.meta['professor_id'], class_id)
            if slot_identifier in self.scraped_slots:
                return None
            else:
                self.scraped_slots.add(slot_identifier)
            yield Slot(
                lesson_type=response.meta['lesson_type'],
                day=day,
                start_time=start_time,
                duration=duration,
                location=response.meta['location'],
                is_composed=response.meta['is_composed'],
                professor_id=response.meta['professor_id'],
                class_id=get_class_id(response.meta['course_unit_id'], response.meta['class_name']),
                last_updated=datetime.now(),
            )
        else:
            yield None
        