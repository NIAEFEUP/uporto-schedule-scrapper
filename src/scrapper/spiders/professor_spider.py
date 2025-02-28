import scrapy
import json
from scrapy.http import Request
from scrapper.settings import START_YEAR
from ..database.Database import Database
from ..items import Professor, CourseUnitProfessor

class ProfessorSpider(scrapy.Spider):
    name = "professors"
    allowed_domains = ['sigarra.up.pt']
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

        self.log(f"Crawling {len(self.course_units)} class units")

        for course_unit_id, recent_occurrence, faculty_id in self.course_units:
            yield Request(
                url=f"https://sigarra.up.pt/feup/pt/mob_ucurr_geral.outras_ocorrencias?pv_ocorrencia_id={recent_occurrence}",
                meta={
                    'course_unit_id': course_unit_id,
                    'faculty_id': faculty_id,
                    'recent_occr': recent_occurrence
                },
                callback=self.extract_instances,
                errback=self.handle_error
            )

    def extract_instances(self, response):
        try:
            data = json.loads(response.body)
        except json.JSONDecodeError:
            self.log("Failed to decode JSON response", level=scrapy.log.ERROR)
            return

        for instance in data:
            if instance.get('ano_letivo', 0) >= START_YEAR:
                instance_id = instance.get('id')
                if instance_id:
                    yield Request(
                        url=f"https://sigarra.up.pt/{response.meta['faculty_id']}/pt/mob_ucurr_geral.perfil?pv_ocorrencia_id={instance_id}",
                        meta={
                            'course_unit_id': response.meta['course_unit_id'],
                            'faculty_id': response.meta['faculty_id'],
                            'instance_id': instance_id,
                            'recent_occr': response.meta['recent_occr']
                        },
                        callback=self.parse_uc_info,
                        errback=self.handle_error
                    )

    def parse_uc_info(self, response):
        course_unit_id = response.meta['course_unit_id']
        
        try:
            data = json.loads(response.body)
        except json.JSONDecodeError:
            self.log("Failed to decode JSON response in parse_uc_info", level=scrapy.log.ERROR)
            return

        for slot in data.get('ds', []):
            for professor in slot.get('docentes', []):
                professor_id = professor.get('doc_codigo')
                professor_name = professor.get('nome')
                
                if professor_id and professor_name:
                    # Add professor if not already inserted
                    if professor_id not in self.inserted_teacher_ids:
                        self.inserted_teacher_ids.add(professor_id)
                        yield Professor(id=professor_id, name=professor_name)
                    
                    # Add course-unit professor relation if not already inserted
                    cu_professor_key = f"{course_unit_id}_{professor_id}"
                    if cu_professor_key not in self.cu_professors:
                        if response.meta['recent_occr'] == response.meta['instance_id']:
                            self.cu_professors.add(cu_professor_key)
                            yield CourseUnitProfessor(course_unit_id=course_unit_id, professor_id=professor_id)

    def handle_error(self, failure):
        self.log(f"Request failed: {failure}", level=scrapy.log.ERROR)