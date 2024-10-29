import scrapy
from ..database.Database import Database

class CourseUnitSpider(scrapy.Spider):
    name = "course_unit_group"
    allowed_domains = ['sigarra.up.pt']

    def __init__(self, *args, **kwargs):
        super(CourseUnitSpider, self).__init__(*args, **kwargs)
        self.db = Database()

        sql = """
            SELECT course.id, year, faculty.acronym
            FROM course JOIN faculty 
            ON course.faculty_id = faculty.acronym
        """
        self.db.cursor.execute(sql)
        self.courses = self.db.cursor.fetchall()

    def start_requests(self):
        # For each course lets go to its page
        for course in self.courses:
            course_id, year, faculty_acronym = course
            url = f'https://sigarra.up.pt/{faculty_acronym}/pt/cur_geral.cur_view?pv_ano_lectivo={year}&pv_origem=CUR&pv_tipo_cur_sigla=M&pv_curso_id={course_id}'
            yield scrapy.Request(url=url, callback=self.parse_course_page, meta={'course_id': course_id, 'year': year, 'faculty_acronym': faculty_acronym})

    def parse_course_page(self, response):
        #now that we are there lets get the course plan url 
        plan_link = response.xpath('//h3[text()="Planos de Estudos"]/following-sibling::div//ul/li/a/@href').extract_first()
        if plan_link:
            plan_id = plan_link.split("pv_plano_id=")[1].split("&")[0]
            plan_url = f'https://sigarra.up.pt/{response.meta["faculty_acronym"]}/pt/cur_geral.cur_planos_estudos_view?pv_plano_id={plan_id}&pv_ano_lectivo={response.meta["year"]}&pv_tipo_cur_sigla=M'
            yield scrapy.Request(url=plan_url, callback=self.parse_course_plan, meta=response.meta)

    def parse_course_plan(self, response):
        #ok we are in the course plan page lets get the information we need from the group tables
        group_divs = response.xpath('//div[contains(@id, "div_id_")]')
        for group_div in group_divs:
            group_title = group_div.xpath('.//h3/text()').extract_first()
            if group_title:
                group_title = group_title.strip()

                group = None
                if "Competências Transversais" in group_title:
                    group = 'Competência Transversal'
                    print("Competência Transversal")
                elif "Grupo" in group_title:
                    group = 'Optativa'
                if group:
                    course_rows = group_div.xpath('.//table[contains(@class, "dadossz")]/tr')
                    for row in course_rows:
                        name = row.xpath('.//td[@class="t"]/a/text()').extract_first()
                        link = row.xpath('.//td[@class="t"]/a/@href').extract_first() #this link is crucial because it has the course unit id
                        if link:
                            try:
                                course_unit_id = link.split("pv_ocorrencia_id=")[1].split("&")[0]

                                self.update_course_unit(course_unit_id, group)

                            except IndexError:
                                print(f"Failed to parse course unit ID from link {link}")

    def update_course_unit(self, course_unit_id, group):
        try:
            sql = """
                UPDATE course_unit 
                SET course_group = ? 
                WHERE id = ? 
            """
            self.db.cursor.execute(sql, (group, course_unit_id))
            
            self.db.connection.commit()

            if self.db.cursor.rowcount > 0:
                print(f"Successfully updated course unit {course_unit_id} with group {group}")
            else:
                print(f"No rows updated. Course unit {course_unit_id} may not exist.")

        except Exception as e:
            print(f"Failed to update course unit {course_unit_id} with group {group}. Error: {e}")
