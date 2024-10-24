import scrapy
from ..database.Database import Database

class CourseUnitGroupSpider(scrapy.Spider):
    name = "course_unit_group"
    allowed_domains = ['sigarra.up.pt']

    def __init__(self, *args, **kwargs):
        super(CourseUnitGroupSpider, self).__init__(*args, **kwargs)
        self.db = Database()

        # Execute the SQL query to fetch courses
        sql = """
            SELECT course.id, year, faculty.acronym
            FROM course JOIN faculty 
            ON course.faculty_id= faculty.acronym
        """
        self.db.cursor.execute(sql)
        self.courses = self.db.cursor.fetchall()
        self.db.connection.close()

    def start_requests(self):
        """
        Generate requests to fetch course plan pages for each course.
        """
        for course in self.courses:
            course_id, year, faculty_acronym = course  # Unpacking the tuple
            print(f"Generating request for Course ID: {course_id}, Year: {year}")

            # Build URL to get the course view page
            url = f'https://sigarra.up.pt/{faculty_acronym}/pt/cur_geral.cur_view?pv_ano_lectivo={year}&pv_origem=CUR&pv_tipo_cur_sigla=M&pv_curso_id={course_id}'
            
            yield scrapy.Request(url=url, callback=self.parse_course_page, meta={'course_id': course_id, 'year': year, 'faculty_acronym': faculty_acronym})

    def parse_course_page(self, response):
        """
        Parse the course page to extract the course plan ID (pv_plano_id).
        """
        print(f"Parsing course page for Course ID: {response.meta['course_id']}")

        # Extract the link that contains the plan ID under <h3>Planos de Estudos</h3>
        plan_link = response.xpath('//h3[text()="Planos de Estudos"]/following-sibling::div//ul/li/a/@href').extract_first()

        if plan_link:
            # Extract the `pv_plano_id` from the URL
            plan_id = plan_link.split("pv_plano_id=")[1].split("&")[0]
            print(f"Found Plan ID: {plan_id}")

            # Now build the URL to request the actual course plan page
            course_id = response.meta['course_id']
            year = response.meta['year']
            faculty_acronym = response.meta['faculty_acronym']

            plan_url = f'https://sigarra.up.pt/{faculty_acronym}/pt/cur_geral.cur_planos_estudos_view?pv_plano_id={plan_id}&pv_ano_lectivo={year}&pv_tipo_cur_sigla=M'
            
            yield scrapy.Request(url=plan_url, callback=self.parse_course_plan, meta={'course_id': course_id, 'year': year, 'plan_id': plan_id})

        else:
            print("No Planos de Estudos section found for this course.")

    def parse_course_plan(self, response):
        """
        Parse the course plan page to extract course unit groups and their details.
        """
        print(f"Parsing course plan page for Plan ID: {response.meta['plan_id']}")

        # Extract the divs containing course unit details (e.g., Group of Options or Competências Transversais)
        group_divs = response.xpath('//div[contains(@id, "div_id_")]')
        print(f"Found {len(group_divs)} divs containing course groups.")

        for group_div in group_divs:
            # Extract the group title (h3 or other relevant header within the div)
            group_title = group_div.xpath('.//h3/text()').extract_first()

            if group_title:
                group_title = group_title.strip()
                # Filter for specific groups like "Competências Transversais" or "Grupo de Opção"
                if "Competências Transversais" in group_title or "Grupo de Opção" in group_title:
                    print(f"Processing group: {group_title}")

                    # Extract the course units within the group
                    course_rows = group_div.xpath('.//table[contains(@class, "dadossz")]/tr')
                    for row in course_rows:
                        code = row.xpath('.//td[@class="k"]/text()').extract_first()
                        name = row.xpath('.//td[@class="t"]/a/text()').extract_first()
                        credits = row.xpath('.//td[@class="n"]/text()').extract_first()

                        if name and code:
                            print(f"  Extracted Course Unit - Code: {code}, Name: {name}, Credits: {credits}")

            else:
                print("No title found for this group.")
