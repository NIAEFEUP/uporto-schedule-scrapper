import scrapy
import hashlib
from ..items import CourseGroup, CUCG
from ..database.Database import Database


class CourseUnitSpider(scrapy.Spider):
    name = "course_unit_group" #This is the name of the table in the database it will be used for some queries
    allowed_domains = ['sigarra.up.pt'] #Domain we are going to scrape

    def __init__(self, *args, **kwargs):
        print("Initializing CourseUnitSpider...")
        super(CourseUnitSpider, self).__init__(*args, **kwargs)
        self.db = Database() 

        # All this is just to get the courses from the database

        sql = """
            SELECT course.id, year, faculty.acronym
            FROM course JOIN faculty                                
            ON course.faculty_id = faculty.acronym
        """
        
        self.db.cursor.execute(sql)
        self.courses = self.db.cursor.fetchall()           


    def start_requests(self): #For every course make request to the course page
        print("Starting requests...")
        for course in self.courses:         
            course_id, year, faculty_acronym = course
            url = f'https://sigarra.up.pt/{faculty_acronym}/pt/cur_geral.cur_view?pv_ano_lectivo={year}&pv_origem=CUR&pv_tipo_cur_sigla=M&pv_curso_id={course_id}'
            yield scrapy.Request(url=url, callback=self.parse_course_page, meta={'course_id': course_id, 'year': year, 'faculty_acronym': faculty_acronym})

    def parse_course_page(self, response): #Scrape the course page , get the plan link and make request to the plan page
        plan_link = response.xpath('//h3[text()="Planos de Estudos"]/following-sibling::div//ul/li/a/@href').extract_first()
        if plan_link:
            plan_id = plan_link.split("pv_plano_id=")[1].split("&")[0]
            plan_url = f'https://sigarra.up.pt/{response.meta["faculty_acronym"]}/pt/cur_geral.cur_planos_estudos_view?pv_plano_id={plan_id}&pv_ano_lectivo={response.meta["year"]}&pv_tipo_cur_sigla=M'
            yield scrapy.Request(url=plan_url, callback=self.parse_course_plan, meta=response.meta)
        else:
            print(f"No Planos de Estudos link found for course ID: {response.meta['course_id']}")

    #Auxiliary functions for parse_course_plan

    def course_unit_exists_already(self, course_unit_id):
        sql = """
        SELECT count(*) 
        FROM course_unit WHERE id = ?
        """
        self.db.cursor.execute(sql, (course_unit_id,))
        result = self.db.cursor.fetchone()
        return result[0] > 0

    def course_group_index(self, course_id, group_course_id):
        sql = """
        SELECT course_group.id
        FROM course_group 
        WHERE group_course_id = ? 
        AND course_id = ?
        """
        self.db.cursor.execute(sql, (group_course_id, course_id))
        result = self.db.cursor.fetchone()
        if result:
            return result[0]
        return None

    def get_next_group_id(self):
        sql = """
        SELECT MAX(id) FROM course_group
        """
        self.db.cursor.execute(sql)
        result = self.db.cursor.fetchone()
        if  result[0]:
            return result[0] + 1
        return 1

    def parse_course_plan(self, response): #Scrape the course plan page to get course groups and the course units in each group then just yield the items
        group_divs = response.xpath('//div[contains(@id, "div_id_")]')
        course_id = response.meta['course_id']

        for group_div in group_divs:
            group_title = group_div.xpath('.//h3/text()').extract_first()
            if group_title:
                group_name = group_title.strip()
                div_id = group_div.xpath('./@id').extract_first().split("_")[2]
                print(f"div id is {div_id}")
                course_rows = group_div.xpath('.//table[contains(@class, "dadossz")]/tr')
                for row in course_rows:
                    name = row.xpath('.//td[@class="t"]/a/text()').extract_first()
                    link = row.xpath('.//td[@class="t"]/a/@href').extract_first()
                    if link:
                        try:
                            course_unit_id = link.split("pv_ocorrencia_id=")[1].split("&")[0]

                            if self.course_unit_exists_already(course_unit_id):
                                # Yield CourseGroup item
                                course_group_id = self.course_group_index( course_id, div_id)
                                if not course_group_id:
                                    course_group_id = self.get_next_group_id()
                                    course_group_item = CourseGroup(
                                        id=course_group_id,
                                        name=group_name,
                                        course_id=course_id,
                                        group_course_id=div_id

                                    )
                                    yield course_group_item 

                                # Yield CUCG item 
                                course_unit_course_group_item = CUCG(
                                    course_unit_id=course_unit_id,
                                    course_group_id=course_group_id,
                                )
                                yield course_unit_course_group_item
                            else:
                                print(f"Course unit ID {course_unit_id} not found in database.")
                        except IndexError:
                            self.logger.warning(f"Failed to parse course unit ID from link {link}")
                    else:
                        print(f"No link found for course unit in group: {group_name}")