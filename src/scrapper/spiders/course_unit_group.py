import scrapy
import hashlib
from ..items import CourseGroup, CourseUnitGroup
from ..database.Database import Database


class CourseUnitGroupSpider(scrapy.Spider):
    name = "course_unit_group" #This is the name of the table in the database it will be used for some queries
    allowed_domains = ['sigarra.up.pt'] #Domain we are going to scrape
    
    course_groups = set()
    course_unit_course_groups = set() 

    def __init__(self, *args, **kwargs):
        print("Initializing CourseUnitSpider...")
        super(CourseUnitGroupSpider, self).__init__(*args, **kwargs)
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

    def get_next_group_id(self):
        sql = """
        SELECT MAX(id) FROM course_group
        """
        self.db.cursor.execute(sql)
        result = self.db.cursor.fetchone()
        if  result[0]:
            return result[0] + 1
        return 1


    def get_year_semester(self, course_unit_id):

        db = Database() 
        sql= """
        SELECT course_metadata.course_unit_year, semester
        FROM course_unit
        JOIN course_metadata ON course_metadata.course_unit_id = course_unit.id
        WHERE course_unit.id = ?
        """
        db.cursor.execute(sql, (course_unit_id,))
        result = db.cursor.fetchone()
        db.connection.close()
        return result
    
    def parse_course_plan(self, response): #Scrape the course plan page to get course groups and the course units in each group then just yield the items
        group_divs = response.xpath('//div[contains(@id, "div_id_")]')
        course_id = response.meta['course_id']
        
        for group_div in group_divs:
            group_title = group_div.xpath('.//h3/text()').extract_first()
            if group_title:
                group_name = group_title.strip()
                div_id = group_div.xpath('./@id').extract_first().split("_")[2]
                course_rows = group_div.xpath('.//table[contains(@class, "dadossz")]/tr')
                for row in course_rows:
                    link = row.xpath('.//td[@class="t"]/a/@href').extract_first()
                    if link:
                        try:
                            course_unit_id = link.split("pv_ocorrencia_id=")[1].split("&")[0]
                            
                            result = self.get_year_semester(course_unit_id)
                            if result:
                                semester = result[1]
                                year = result[0]
                                if semester is not None and year is not None:
                                    try:
                                        semester = int(semester)
                                        year = int(year)
                                    except ValueError:
                                        self.logger.warning(f"Invalid semester or year value for course unit ID: {course_unit_id}, semester: {semester}, year: {year}")
                                        continue

                                    cg_id = int(f"{div_id}{year}{semester}")
                                    if(cg_id not in self.course_groups):
                                        self.course_groups.add(cg_id)
                                        course_group_item = CourseGroup(
                                            id=cg_id,
                                            name=group_name,
                                            course_id=course_id,
                                            semester=semester,
                                            year=year
                                        )
     
                                        yield course_group_item
                                    cucg_hash = hashlib.md5(f"{course_unit_id}{cg_id}".encode()).hexdigest()
                                    if cucg_hash not in self.course_unit_course_groups : #This check makes no sense because it is checking if the course unit exists, but it should check if the course unit group exists
                                        self.course_unit_course_groups.add(cucg_hash)
                                        course_unit_course_group_item = CourseUnitGroup(
                                            course_unit_id=course_unit_id,
                                            course_group_id=cg_id,
                                        )
                                        yield course_unit_course_group_item
                        except IndexError:
                            self.logger.warning(f"Failed to parse course unit ID from link {link}")
       