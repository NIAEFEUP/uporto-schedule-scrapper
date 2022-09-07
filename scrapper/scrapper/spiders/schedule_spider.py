""" import getpass
import scrapy
from datetime import datetime
from scrapy.http import Request, FormRequest
import urllib.parse
import json

from ..con_info import ConInfo
from ..items import Schedule


class ScheduleSpider(scrapy.Spider):
    name = "schedules"
    allowed_domains = ['sigarra.up.pt']
    login_page_base = 'https://sigarra.up.pt/feup/pt/mob_val_geral.autentica'
    days = {'Segunda': 0, 'Terça': 1, 'Quarta': 2,
            'Quinta': 3, 'Sexta': 4, 'Sábado': 5}
    password = None

    def __init__(self, category=None, *args, **kwargs):
        super(ScheduleSpider, self).__init__(*args, **kwargs)

    def format_login_url(self):
        return '{}?{}'.format(self.login_page_base, urllib.parse.urlencode({
            'pv_login': self.user,
            'pv_password': self.password
        }))

    def start_requests(self):
        "This function is called before crawling starts."

        if self.password is None:
            self.password = getpass.getpass(prompt='Password: ', stream=None)

        yield Request(url=self.format_login_url(), callback=self.check_login_response)

    def check_login_response(self, response):
        "Check the response returned by a login request to see if we are
        successfully logged in. Since we used the mobile login API endpoint,
        we can just check the status code.
        "

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
        con_info = ConInfo()
        with con_info.connection.cursor() as cursor:
            sql = "SELECT `id`, `schedule_url` FROM `course_unit` WHERE schedule_url IS NOT NULL"
            cursor.execute(sql)
            self.class_units = cursor.fetchall()

        con_info.connection.close()

        self.log("Crawling {} class units".format(len(self.class_units)))
        for class_unit in self.class_units:
            yield Request(
                url=class_unit[1],
                meta={'id': class_unit[0]},
                callback=self.extractSchedule)

    def extractSchedule(self, response):
        # Check if there is no schedule available
        if response.xpath('//div[@id="erro"]/h2/text()').extract_first() == "Sem Resultados":
            yield None

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
                        yield self.extractClassSchedule(response, cur_col, cur_day, hour, int(class_duration) / 2,
                                                        response.meta['id'])

                hour += 0.5

        # Overlapping classes
        for row in response.xpath('//table[@class="dados"]/tr[not(th)]'):
            yield self.extractOverlappingClassSchedule(response, row, response.meta['id'])

    def extractClassSchedule(self, response, cell, day, start_time, duration, id):
        lesson_type = cell.xpath(
            'b/text()').extract_first().strip().replace('(', '', 1).replace(')', '', 1)

        table = cell.xpath('table/tr')
        location = table.xpath('td/a/text()').extract_first()
        teacher = table.xpath('td[@class="textod"]//a/text()').extract_first()

        clazz = cell.xpath('span/a')
        class_name = clazz.xpath('text()').extract_first()
        class_url = clazz.xpath('@href').extract_first()

        # If true, this means the class is composed of more than one class
        # And an additional request must be made to obtain all classes
        if "hor_geral.composto_desc" in class_url:
            return response.follow(class_url,
                                   dont_filter=True,
                                   meta={'id': id, 'lesson_type': lesson_type, 'start_time': start_time,
                                         'teacher_acronym': teacher, 'location': location, 'day': day,
                                         'composed_class_name': class_name, 'duration': duration},
                                   callback=self.extractComposedClasses)

        return Schedule(
            course_unit_id=id,
            lesson_type=lesson_type,
            day=day,
            start_time=start_time,
            duration=duration,
            teacher_acronym=teacher,
            location=location,
            class_name=class_name,
            last_updated=datetime.now()
        )

    def extractComposedClasses(self, response):
        class_names = response.xpath(
            '//div[@id="conteudoinner"]/li/a/text()').extract()

        for class_name in class_names:
            yield Schedule(
                course_unit_id=response.meta['id'],
                lesson_type=response.meta['lesson_type'],
                day=response.meta['day'],
                start_time=response.meta['start_time'],
                duration=response.meta['duration'],
                teacher_acronym=response.meta['teacher_acronym'],
                location=response.meta['location'],
                composed_class_name=response.meta['composed_class_name'],
                class_name=class_name,
                last_updated=datetime.now()
            )

    def extractOverlappingClassSchedule(self, response, row, id):
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
        teacher = row.xpath('td[5]/a/text()').extract_first()

        clazz = row.xpath('td[6]/a')
        class_url = clazz.xpath('@href').extract_first()
        class_name = clazz.xpath('text()').extract_first()

        # If true, this means the class is composed of more than one class
        # And an additional request must be made to obtain all classes
        if "hor_geral.composto_desc" in class_url:
            return response.follow(class_url,
                                   dont_filter=True,
                                   meta={'id': id, 'lesson_type': lesson_type, 'start_time': start_time,
                                         'teacher_acronym': teacher, 'location': location, 'day': day,
                                         'composed_class_name': class_name},
                                   callback=self.extractDurationFromComposedOverlappingClasses)

        return response.follow(class_url,
                               dont_filter=True,
                               meta={'id': id, 'lesson_type': lesson_type, 'start_time': start_time,
                                     'teacher_acronym': teacher, 'location': location, 'day': day,
                                     'class_name': class_name},
                               callback=self.extractDurationFromOverlappingClass)

    def extractDurationFromComposedOverlappingClasses(self, response):
        classes = response.xpath('//div[@id="conteudoinner"]/li/a')

        for clazz in classes:
            class_name = clazz.xpath('./text()').extract_first()
            class_url = clazz.xpath('@href').extract_first()

            yield response.follow(class_url,
                                  dont_filter=True,
                                  meta={
                                      'id': response.meta['id'], 'lesson_type': response.meta['lesson_type'],
                                      'start_time': response.meta['start_time'], 'teacher_acronym': response.meta['teacher_acronym'],
                                      'location': response.meta['location'], 'day': response.meta['day'],
                                      'composed_class_name': response.meta['composed_class_name'], 'class_name': class_name
                                  },
                                  callback=self.extractDurationFromOverlappingClass)

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

        yield Schedule(
            course_unit_id=response.meta['id'],
            lesson_type=response.meta['lesson_type'],
            day=day,
            start_time=start_time,
            duration=duration,
            teacher_acronym=response.meta['teacher_acronym'],
            location=response.meta['location'],
            class_name=response.meta['class_name'],
            last_updated=datetime.now(),
            composed_class_name=response.meta['composed_class_name'] if 'composed_class_name' in response.meta else None
        )
 """