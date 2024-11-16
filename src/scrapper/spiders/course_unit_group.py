import scrapy
import hashlib
from ..items import CourseGroup, CUCG
from ..database.Database import Database


class CourseUnitSpider(scrapy.Spider):
    name = "course_unit_group"
    allowed_domains = ['sigarra.up.pt']

    def __init__(self, *args, **kwargs):
        print("Initializing CourseUnitSpider...")
        super(CourseUnitSpider, self).__init__(*args, **kwargs)
        self.db = Database()

        sql = """
            SELECT course.id, year, faculty.acronym
            FROM course JOIN faculty 
            ON course.faculty_id = faculty.acronym
        """
        print("Executing SQL query to fetch courses...")
        self.db.cursor.execute(sql)
        self.courses = self.db.cursor.fetchall()
        print(f"Fetched {len(self.courses)} courses from the database.")

    def start_requests(self):
        print("Starting requests...")
        for course in self.courses:
            course_id, year, faculty_acronym = course
            print(f"Processing course: {course_id}, Year: {year}, Faculty: {faculty_acronym}")
            url = f'https://sigarra.up.pt/{faculty_acronym}/pt/cur_geral.cur_view?pv_ano_lectivo={year}&pv_origem=CUR&pv_tipo_cur_sigla=M&pv_curso_id={course_id}'
            yield scrapy.Request(url=url, callback=self.parse_course_page, meta={'course_id': course_id, 'year': year, 'faculty_acronym': faculty_acronym})

    def parse_course_page(self, response):
        print(f"Parsing course page for course ID: {response.meta['course_id']}")
        plan_link = response.xpath('//h3[text()="Planos de Estudos"]/following-sibling::div//ul/li/a/@href').extract_first()
        if plan_link:
            plan_id = plan_link.split("pv_plano_id=")[1].split("&")[0]
            plan_url = f'https://sigarra.up.pt/{response.meta["faculty_acronym"]}/pt/cur_geral.cur_planos_estudos_view?pv_plano_id={plan_id}&pv_ano_lectivo={response.meta["year"]}&pv_tipo_cur_sigla=M'
            print(f"Found plan link: {plan_url}")
            yield scrapy.Request(url=plan_url, callback=self.parse_course_plan, meta=response.meta)
        else:
            print(f"No Planos de Estudos link found for course ID: {response.meta['course_id']}")

    def parse_course_plan(self, response):
        print(f"Parsing course plan for course ID: {response.meta['course_id']}")
        group_divs = response.xpath('//div[contains(@id, "div_id_")]')
        course_id = response.meta['course_id']

        for group_div in group_divs:
            group_title = group_div.xpath('.//h3/text()').extract_first()
            if group_title:
                group_name = group_title.strip()
                print(f"Found group: {group_name} for course ID: {course_id}")
                hash_object = hashlib.md5(group_name.encode('utf-8'))
                hashed_group_name = hash_object.hexdigest()
                numeric_group_id = int(hashed_group_name, 16) % 10**8  
                print(f"Generated numeric group ID: {numeric_group_id}")

                # Yield CourseGroup item
                course_group_item = CourseGroup(
                    id=numeric_group_id,
                    name=group_name,
                    course_id=course_id
                )
                yield course_group_item 

                course_rows = group_div.xpath('.//table[contains(@class, "dadossz")]/tr')
                for row in course_rows:
                    name = row.xpath('.//td[@class="t"]/a/text()').extract_first()
                    link = row.xpath('.//td[@class="t"]/a/@href').extract_first()
                    if link:
                        try:
                            course_unit_id = link.split("pv_ocorrencia_id=")[1].split("&")[0]
                            print(f"Found course unit ID: {course_unit_id} in group: {group_name}")
                            # Yield CUCG item 
                            course_unit_course_group_item = CUCG(
                                course_unit_id=course_unit_id,
                                course_group_id=numeric_group_id,
                            )
                            yield course_unit_course_group_item
                        except IndexError:
                            self.logger.warning(f"Failed to parse course unit ID from link {link}")
                            print(f"Failed to parse course unit ID from link {link}")
                    else:
                        print(f"No link found for course unit in group: {group_name}")