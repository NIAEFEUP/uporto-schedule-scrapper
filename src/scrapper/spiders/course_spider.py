
import scrapy
from datetime import datetime
from urllib.parse import urlparse, parse_qs
from configparser import ConfigParser, ExtendedInterpolation

from scrapper.utils.DateUtils import get_scrapper_year
from scrapper.settings import CONFIG, YEAR
from ..items import Course
from ..database.Database import Database
from dotenv import dotenv_values

class CourseSpider(scrapy.Spider):
    name = "courses"
    allowed_domains = ['sigarra.up.pt']
    login_page = 'https://sigarra.up.pt/feup/pt/'

    bachelors_url = "https://www.up.pt/portal/en/study/bachelors-and-integrated-masters-degrees/courses/"
    masters_url = "https://www.up.pt/portal/en/study/masters-degrees/courses/"
    doctors_url = "https://www.up.pt/portal/en/study/doctorates/courses/"
    start_urls = [bachelors_url, masters_url, doctors_url]
    
    def open_config(self):
        """
        Reads and saves the configuration file. 
        """
        config_file = "./config.ini"
        self.config = ConfigParser(interpolation=ExtendedInterpolation())
        self.config.read(config_file) 

    def get_year(self):
        year = CONFIG[YEAR]
        if not year:
            return get_scrapper_year()
        return int(year)   

    # Get's the first letter of the course type and set it to upper case. 
    
    def parse(self, response):
        self.open_config()

        hrefs = response.xpath('//*[@id="courseListComponent"]/div/dl/dd/ul/li/a/@href').extract()  
        for faculty_html in hrefs: 
            params = faculty_html.split("/")
            url = f"https://sigarra.up.pt/{params[-3]}/pt/cur_geral.cur_view?pv_ano_lectivo={self.get_year()}&pv_curso_id={params[-2]}"
            yield scrapy.Request(url= url, callback=self.get_course, meta={'faculty_acronym': params[-3]})
    
    def get_acronym(self, response):
        acronym = response.xpath('//td[text()="Sigla: "]/following-sibling::td/text()').get()
        if not acronym:
            acronym = response.xpath('//td[text()="Acronym: "]/following-sibling::td/text()').get()
        return acronym

    def get_course(self, response):
        for courseHtml in response.css('body'):
            if courseHtml.xpath(
                    '//*[@id="conteudoinner"]/div[1]/a').extract_first() is not None:  # tests if this page points to another one
                continue
            
            # Check if the course has an acronym
            # Some pages don't have an acronym, usually because they are not available for the current year
            acronym = self.get_acronym(response)

            
            if not acronym:
                continue

            course_type= response.xpath('//td[text()="Tipo de curso/ciclo de estudos: "]/following-sibling::td/text()').get()

            sigarra_id = response.url.split('=')[-1]
            course = Course(
                id = sigarra_id,
                faculty_id = response.meta['faculty_acronym'],    # New parameter 
                name = response.xpath('//*[@id="conteudoinner"]/h1[2]').extract()[0][4:-5],
                acronym = acronym,
                course_type = course_type,
                year = self.get_year(),
                url = response.url,
                plan_url = f"cur_geral.cur_planos_estudos_view?pv_plano_id={sigarra_id}&pv_ano_lectivo={self.get_year()}",
                last_updated=datetime.now(),
            )

            yield course
