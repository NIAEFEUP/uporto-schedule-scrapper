import scrapy
from ..database.Database import Database

class CourseUnitSpider(scrapy.Spider):
    name = "course_unit_group"
    allowed_domains = ['sigarra.up.pt']

    def __init__(self, *args, **kwargs):
        super(CourseUnitSpider, self).__init__(*args, **kwargs)
        self.db = Database()

        # Fetch courses to process
        sql = """
            SELECT course.id, year, faculty.acronym
            FROM course JOIN faculty 
            ON course.faculty_id = faculty.acronym
        """
        self.db.cursor.execute(sql)
        self.courses = self.db.cursor.fetchall()

    def start_requests(self):
        for course in self.courses:
            course_id, year, faculty_acronym = course
            url = f'https://sigarra.up.pt/{faculty_acronym}/pt/cur_geral.cur_view?pv_ano_lectivo={year}&pv_origem=CUR&pv_tipo_cur_sigla=M&pv_curso_id={course_id}'
            yield scrapy.Request(url=url, callback=self.parse_course_page, meta={'course_id': course_id, 'year': year, 'faculty_acronym': faculty_acronym})

    def parse_course_page(self, response):
        plan_link = response.xpath('//h3[text()="Planos de Estudos"]/following-sibling::div//ul/li/a/@href').extract_first()
        if plan_link:
            plan_id = plan_link.split("pv_plano_id=")[1].split("&")[0]
            plan_url = f'https://sigarra.up.pt/{response.meta["faculty_acronym"]}/pt/cur_geral.cur_planos_estudos_view?pv_plano_id={plan_id}&pv_ano_lectivo={response.meta["year"]}&pv_tipo_cur_sigla=M'
            yield scrapy.Request(url=plan_url, callback=self.parse_course_plan, meta=response.meta)

    def parse_course_plan(self, response):
        group_divs = response.xpath('//div[contains(@id, "div_id_")]')
        for group_div in group_divs:
            group_title = group_div.xpath('.//h3/text()').extract_first()
            if group_title:
                group_title = group_title.strip()

                # Determine the course unit group based on the title
                group = None
                if "Competência Transversal" in group_title:
                    group = 'Competência Transversal'
                elif "Optativa" in group_title:
                    group = 'Optativa'
                if group:
                    course_rows = group_div.xpath('.//table[contains(@class, "dadossz")]/tr')
                    for row in course_rows:
                        code = row.xpath('.//td[@class="k"]/text()').extract_first()

                        if code:
                            self.update_course_unit(code, group, response.meta['course_id'], response.meta['year'])

    def update_course_unit(self, code, group, course_id, year):
        """Update an existing course unit with the group and other details."""
        sql = """
            UPDATE course_unit 
            SET course_group = ? 
            WHERE id = ? AND year = ? AND course_id = ?
        """
        self.db.cursor.execute(sql, (group, code, year, course_id))
        self.db.connection.commit()
