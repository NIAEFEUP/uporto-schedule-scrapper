import getpass
import hashlib
import re
import scrapy
from datetime import datetime
from scrapy.http import Request, FormRequest
import urllib.parse
from configparser import ConfigParser, ExtendedInterpolation
import json
from datetime import time

from scrapper.settings import CONFIG, START_YEAR

from ..database.Database import Database
from ..items import Professor, CourseUnitProfessor

class ProfessorSpider(scrapy.Spider):
    name = "professors"
    allowed_domains = ['sigarra.up.pt']
    days = {'Segunda-feira': 0, 'Terça-feira': 1, 'Quarta-feira': 2,
            'Quinta-feira': 3, 'Sexta-feira': 4, 'Sábado': 5}
    professor_name_pattern = "\d+\s-\s[A-zÀ-ú](\s[A-zÀ-ú])*"
    inserted_teacher_ids = set()
    cu_professors = set()


    def start_requests(self):
        db = Database()
        sql = """
            SELECT cu.id, cu.recent_occr, f.acronym
            FROM course_unit cu
            JOIN course_course_unit ccu ON cu.id = ccu.course_unit_id
            JOIN course c ON ccu.course_id = c.id
            JOIN faculty f ON c.faculty_id = f.acronym;

        """
        db.cursor.execute(sql)
        self.course_units = db.cursor.fetchall()

        db.connection.close()

        self.log("Crawling {} class units".format(len(self.course_units)))

        for course_unit in self.course_units:
            course_unit_id = course_unit[0]
            recent_occurrence = course_unit[1]
            faculty_id = course_unit[2]
            

            yield scrapy.http.Request(
                url="https://sigarra.up.pt/feup/pt/mob_ucurr_geral.outras_ocorrencias?pv_ocorrencia_id={}".format(recent_occurrence),
                meta={'course_unit_id': course_unit_id, 'faculty_id': faculty_id, 'recent_occr': recent_occurrence},
                callback=self.extractInstances
            )
            
    def extractInstances(self, response):
            data = json.loads(response.body)
            
            for instance in data:
                if(instance.get('ano_letivo')  >= START_YEAR):
                    instance_id = instance.get('id')
                    if instance_id:
                        yield Request(
                            url=f"https://sigarra.up.pt/{response.meta['faculty_id']}/pt/mob_ucurr_geral.perfil?pv_ocorrencia_id={instance_id}",
                            meta={'course_unit_id': response.meta['course_unit_id'], 'faculty_id': response.meta['faculty_id'], 'instance_id': instance_id, 'recent_occr': response.meta['recent_occr']},
                            callback=self.parseUCInfo,
                            errback=self.func
                        )

    def func(self, error):
        print("An error has occurred: ", error)
        return

    def parseUCInfo(self, response):
        course_unit_id = response.meta['course_unit_id']
        
        # Parse JSON response
        data = json.loads(response.body)
        
        # Extract professors from the ds field in JSON data
        slots = data.get('ds', [])
        
        for slot in slots:
            professors = slot.get('docentes', [])
            for professor in professors:
                professor_id = professor.get('doc_codigo')
                professor_name = professor.get('nome')
                if professor_id and professor_name:
                        if professor_id not in self.inserted_teacher_ids:
                            self.inserted_teacher_ids.add(professor_id)
                            yield Professor(
                                id=professor_id,
                                name=professor_name
                            )
                        hash = hashlib.sha256(str(course_unit_id).encode('utf-8') + str(professor_id).encode('utf-8')).hexdigest()
                        if hash not in self.cu_professors:
                            self.cu_professors.add(hash)
                            if(response.meta['recent_occr'] == response.meta['instance_id']):
                                yield CourseUnitProfessor(
                                course_unit_id = course_unit_id,
                                professor_id = professor_id
                                )

