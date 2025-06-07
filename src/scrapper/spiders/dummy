import scrapy
import hashlib
from ..items import  CourseUnitGroup
from ..database.Database import Database
from urllib.parse import urlparse, parse_qs, urlencode
import re


class CourseUnitGroupSpider(scrapy.Spider):
    name = "course_unit_groups" #This is the name of the table in the database it will be used for some queries
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


    async def start(self): #For every course make request to the course page
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
            
    


    def parse_course_plan(self, response):
        group_divs = response.xpath('//div[contains(@id, "div_id_")]')
        course_id = response.meta['course_id']

        for group_div in group_divs:
            group_title = group_div.xpath('.//h3/text()').extract_first()
            if group_title:
                group_name = group_title.strip()
                div_id = group_div.xpath('./@id').extract_first().split("_")[2]

                # Extract the year from the corresponding <a> tag
                year_element = response.xpath(f'//a[contains(@id, "bloco_acurr_ShowOrHide") and contains(@href, "{div_id}")]')
                year_text = year_element.xpath('normalize-space(text())').get()
                year = year_text.split("º")[0] if year_text else "Unknown"

                course_rows = group_div.xpath('.//table[contains(@class, "dadossz")]/tr')
                if(len(course_rows) == 1):
                    continue
                for row in course_rows:
                    link = row.xpath('.//td[@class="t"]/a/@href').extract_first()
                    if link:
                        year = row.xpath('.//td[5]/text()').get().split("º")[0].strip()
                        if not year:
                            self.logger.warning(f"No year found for row: {row}")
                            year = "Unknown" 
                        try:
                            course_unit_id = link.split("pv_ocorrencia_id=")[1].split("&")[0]
                            course_unit_url = f'https://sigarra.up.pt/feup/pt/ucurr_geral.ficha_uc_view?pv_ocorrencia_id={course_unit_id}'
                            yield scrapy.Request(
                                url=course_unit_url,
                                callback=self.parse_course_unit_page,
                                meta={
                                    'course_id': course_id,
                                    'group_name': group_name,
                                    'course_unit_id': course_unit_id,
                                    'div_id': div_id,
                                    'year': year  # Include the extracted year
                                }
                            )
                        except IndexError:
                            self.logger.warning(f"Failed to parse course unit ID from link {link}")
                    else:
                        self.logger.warning(f"No link found for course unit in group: {group_name}")
        pattern = re.compile(r'^div_\d+_id_')
        divs = response.xpath('//div[starts-with(@id, "div_") and contains(@id, "_id_")]')
        for group_div in divs:
            id = group_div.xpath('@id').get()
            if id and pattern.match(id):
                group_title = group_div.xpath('.//h3/text()').extract_first()
                if group_title:
                    group_name = group_title.strip()
                    div_id = group_div.xpath('./@id').extract_first().split("_")[3]

                    # Extract the year from the corresponding <a> tag
                    year_element = response.xpath(f'//a[contains(@id, "bloco_acurr_ShowOrHide") and contains(@href, "{div_id}")]')
                    year_text = year_element.xpath('normalize-space(text())').get()
                    year = year_text.split("º")[0] if year_text else "Unknown"

                    course_rows = group_div.xpath('.//table[contains(@class, "dadossz")]/tr')
                    if(len(course_rows) == 1):
                        continue
                    for row in course_rows:
                        link = row.xpath('.//td[@class="t"]/a/@href').extract_first()
                        if link:
                            year = row.xpath('.//td[5]/text()').get().split("º")[0].strip()
                            if not year:
                                self.logger.warning(f"No year found for row: {row}")
                                year = "Unknown" 
                            try:
                                course_unit_id = link.split("pv_ocorrencia_id=")[1].split("&")[0]
                                course_unit_url = f'https://sigarra.up.pt/feup/pt/ucurr_geral.ficha_uc_view?pv_ocorrencia_id={course_unit_id}'
                                yield scrapy.Request(
                                    url=course_unit_url,
                                    callback=self.parse_course_unit_page,
                                    meta={
                                        'course_id': course_id,
                                        'group_name': group_name,
                                        'course_unit_id': course_unit_id,
                                        'div_id': div_id,
                                        'year': year  # Include the extracted year
                                    }
                                )
                            except IndexError:
                                self.logger.warning(f"Failed to parse course unit ID from link {link}")
                        else:
                            self.logger.warning(f"No link found for course unit in group: {group_name}")


        
    def parse_course_unit_page(self, response): #Scrape the course unit page to get the course unit name and acronym
        outras_ocorrencias_link = response.xpath('//a[text()="Outras ocorrências"]/@href').get()
        if outras_ocorrencias_link:
            course_unit_id = parse_qs(urlparse(outras_ocorrencias_link).query)['pv_ucurr_id'][0]
        else:
            self.logger.warning(f"No 'Outras ocorrências' link found for course unit in response URL: {response.url}")
            return
        Instance = response.css('#conteudoinner > h2::text').extract_first()
        semester = Instance[24:26].strip()
        
        yield CourseUnitGroup(
              id = response.meta['div_id'],
              name = response.meta['group_name'],
          )
        
        sql = """
            SELECT id FROM course_course_unit
            WHERE course_unit_id = ? AND course_id = ? AND year = ? AND semester = ?
            """
        self.db.cursor.execute(sql, (course_unit_id, response.meta['course_id'], response.meta['year'], semester))
        course_course_unit_id = self.db.cursor.fetchone()
        if course_course_unit_id:
            course_course_unit_id = course_course_unit_id[0]
        else:
            print("course_course_unit_id not found.")
            return
        try:
            sql = """
                INSERT INTO course_course_unit_group (course_course_unit_id, course_unit_group_id)
                VALUES (?, ?)
            """
            params = (course_course_unit_id, response.meta['div_id'])

            self.db.cursor.execute(sql, params)
            self.db.connection.commit()
        except:
            print("ERROR in insert course_course_unit_group")