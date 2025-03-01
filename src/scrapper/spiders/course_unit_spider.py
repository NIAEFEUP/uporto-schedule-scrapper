import getpass
import scrapy

import sqlite3

from scrapy.http import Request, FormRequest
from urllib.parse import urlparse, parse_qs, urlencode
from configparser import ConfigParser, ExtendedInterpolation
from datetime import datetime
import pandas as pd
import logging
import json

from scrapper.settings import CONFIG

from ..database.Database import Database
from ..items import CourseUnit, CourseCourseUnit, CourseUnitProfessor, Professor
import hashlib

class CourseUnitSpider(scrapy.Spider):
    name = "course_units"
    course_units_ids = set()
    course_courses_units_hashes = set()
    prof_ids = set()
    course_unit_professors = set()

    def start_requests(self):
        "This function is called before crawling starts."
        return self.courseRequests()

    def courseRequests(self):
        print("Gathering course units") 
        db = Database() 

        sql = """
            SELECT course.id, year, faculty.acronym 
            FROM course JOIN faculty 
            ON course.faculty_id= faculty.acronym
        """
        db.cursor.execute(sql)
        self.courses = db.cursor.fetchall()
        db.connection.close()

        self.log("Crawling {} courses".format(len(self.courses)))

        for course in self.courses:
            yield scrapy.http.Request(
                url='https://sigarra.up.pt/{}/pt/ucurr_geral.pesquisa_ocorr_ucs_list?pv_ano_lectivo={}&pv_curso_id={}'.format(
                    course[2], course[1], course[0]),
                meta={'course_id': course[0]},
                callback=self.extractSearchPages)
            
    def extractSearchPages(self, response):
        last_page_url = response.css(
            ".paginar-saltar-barra-posicao > div:last-child > a::attr(href)").extract_first()
        last_page = int(parse_qs(urlparse(last_page_url).query)[
            'pv_num_pag'][0]) if last_page_url is not None else 1
        for x in range(1, last_page + 1):
            yield scrapy.http.Request(
                url=response.url + "&pv_num_pag={}".format(x),
                meta=response.meta,
                callback=self.extractCourseUnits)

    def extractCourseUnits(self, response):
        course_units_table = response.css("table.dados .d")

        for course_unit_row in course_units_table:
            yield scrapy.http.Request(
                url=response.urljoin(course_unit_row.css(
                    ".t > a::attr(href)").extract_first()),
                meta=response.meta,
                callback=self.extractCourseUnitInfo)

    def extractCourseUnitInfo(self, response):
        name = response.xpath(
            '//div[@id="conteudoinner"]/h1[2]/text()').extract_first().strip()

        # Checks if the course unit page is valid.
        # If name == 'Sem Resultados', then it is not.
        if name == 'Sem Resultados':
            return None  # Return None as yielding would continue the program and crash at the next assert

        current_occurence_id = parse_qs(urlparse(response.url).query)['pv_ocorrencia_id'][0]

        # Get the link with text "Outras ocorrências" and extract the course unit ID from its URL
        course_unit_id = parse_qs(urlparse(response.xpath('//a[text()="Outras ocorrências"]/@href').get()).query)['pv_ucurr_id'][0]

        acronym = response.xpath(
            '//div[@id="conteudoinner"]/table[@class="formulario"][1]//td[text()="Sigla:"]/following-sibling::td[1]/text()').extract_first()

        # Some pages have Acronym: instead of Sigla:
        if acronym is None: 
            acronym = response.xpath(
                '//div[@id="conteudoinner"]/table[@class="formulario"][1]//td[text()="Acronym:"]/following-sibling::td[1]/text()').extract_first()

        if acronym is not None:
            acronym = acronym.replace(".", "_")

        url = response.url
        # # If there is no schedule for this course unit
        # if schedule_url is not None:
        #     schedule_url = response.urljoin(schedule_url)

        # Instance has a string that contains both the year and the semester type
        Instance = response.css('#conteudoinner > h2::text').extract_first()

        # Possible types: '1', '2', 'A', 'SP'
        # '1' and '2' represent a semester
        # 'A' represents an annual course unit
        # 'SP' represents a course unit without effect this year
        semester = Instance[24:26].strip()

        # Represents the civil year. If the course unit is taught on the curricular year
        # 2017/2018, then year is 2017.
        year = int(Instance[12:16])

        assert semester == '1S' or semester == '2S' or semester == 'A' or semester == 'SP' \
            or semester == '1T' or semester == '2T' or semester == '3T' or semester == '4T'

        assert year > 2000

      
        if (course_unit_id not in self.course_units_ids):
            self.course_units_ids.add(course_unit_id)
            yield CourseUnit(
                id=course_unit_id,
                name=name,
                acronym=acronym,
                recent_occr=current_occurence_id, # This might be wrong but I fix it later xd just cuz not null
                last_updated=datetime.now()
            )
        
        study_cycles = response.xpath('//h3[text()="Ciclos de Estudo/Cursos"]/following-sibling::table[1]').get()
        if study_cycles is None:
            return
        df = pd.read_html(study_cycles, decimal=',', thousands='.', extract_links="all")[0]
        for (_, row) in df.iterrows():
                if(parse_qs(urlparse(row[0][1]).query).get('pv_curso_id')[0] == str(response.meta['course_id'])):
                    cu = CourseCourseUnit(
                            course_id= parse_qs(urlparse(row[0][1]).query).get('pv_curso_id')[0],
                            course_unit_id=course_unit_id,
                            year=row[3][0],
                            semester=semester,
                            ects=row[5][0]
                            )
                    hash_ccu = hashlib.md5((cu['course_id']+cu['course_unit_id']+cu['year']+ cu['semester']).encode()).hexdigest()
                    if(hash_ccu not in self.course_courses_units_hashes):
                        self.course_courses_units_hashes.add(hash_ccu)
                        yield cu
        yield scrapy.http.Request(
                url="https://sigarra.up.pt/feup/pt/mob_ucurr_geral.outras_ocorrencias?pv_ocorrencia_id={}".format(current_occurence_id),
                meta={'course_unit_id': course_unit_id, 'semester': semester, 'year': year},
                callback=self.extractInstances
            )

                       
                
    def extractInstances(self, response):
        data = json.loads(response.body)
        
        valid_instances = [uc for uc in data if uc.get('ano_letivo') >= response.meta['year']]
        
        today = datetime.now()
        
        month = today.month

        if month >= 9 or month <= 1:
            current_semester = '1S'
        elif month >= 2 and month <= 7:
            current_semester = '2S'
        else:
            current_semester = None 

        def sort_key(uc):
            instance_semester = uc.get('semestre')
            if current_semester and instance_semester and current_semester == instance_semester or instance_semester == 'A':
                return 0  # Current semester instances first
            else:
                return 1  # Other semesters after

        valid_instances = [uc for uc in data if uc.get('ano_letivo') == response.meta['year']]
        valid_instances.sort(key=sort_key)

        max_occr_id = valid_instances[0].get('id') if valid_instances else None
        
        db = Database()
        sql = """
            UPDATE course_unit
            SET recent_occr = ?
            WHERE id = ?
        """
        db.cursor.execute(sql, (max_occr_id, response.meta['course_unit_id']))
        db.connection.commit()
        db.connection.close()