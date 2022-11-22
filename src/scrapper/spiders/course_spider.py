
import scrapy
from datetime import datetime
from urllib.parse import urlparse, parse_qs
from configparser import ConfigParser, ExtendedInterpolation

from ..items import Course
from ..database.Database import Database

class CourseSpider(scrapy.Spider):
    name = "courses"
    allowed_domains = ['sigarra.up.pt']
    login_page = 'https://sigarra.up.pt/feup/pt/'

    bachelors_url = "https://www.up.pt/portal/en/study/bachelors-and-integrated-masters-degrees/courses/"
    masters_url = "https://www.up.pt/portal/en/study/masters-degrees/courses/"
    start_urls = [bachelors_url, masters_url]
    
    def open_config(self):
        """
        Reads and saves the configuration file. 
        """
        config_file = "./config.ini"
        self.config = ConfigParser(interpolation=ExtendedInterpolation())
        self.config.read(config_file) 


    def get_year(self):
        year = self.config['default']['YEAR']
        if not year:
            raise Exception('YEAR variable not specified for parsing in configuration file!')
        return int(year)   


    def parse(self, response):

        hrefs = response.xpath('//*[@id="courseListComponent"]/div/dl/dd/ul/li/a/@href').extract()  
        for faculty_html in hrefs: 
            params = faculty_html.split("/")
            url = f"https://sigarra.up.pt/{params[-3]}/en/cur_geral.cur_view?pv_curso_id={params[-2]}"
            yield scrapy.Request(url= url, callback=self.parse)

    def parse(self, response):
        for courseHtml in response.css('body'):
            if courseHtml.xpath(
                    '//*[@id="conteudoinner"]/div[1]/a').extract_first() is not None:  # tests if this page points to another one
                continue
            
            course = Course(
                # diogo 
                course_id = response.url.split('=')[-1]
                name = response.xpath('//*[@id="conteudoinner"]/h1[2]').extract()[0][4:-5]
                course_type = response.xpath('//*[@id="conteudoinner"]/div[2]/div/div[2]/div[1]/table/tbody/tr[5]/td').extract()


                # xuliane
                acronym = 

            )
            #course = Course(
            #    course_id=int(parse_qs(urlparse(response.url).query)['pv_curso_id'][0]),
            #    name=courseHtml.css('#conteudoinner h1:last-of-type::text').extract_first(),
            #    course_type=response.meta['course_type'],
            #    faculty_id=response.meta['faculty_id'],
            #    acronym=courseHtml.css('span.pagina-atual::text').extract_first()[3:],
            #    url=response.url,
            #    plan_url=response.urljoin(courseHtml.xpath(
            #        '(//h3[text()="Planos de Estudos"]/following-sibling::div[1]//a)[1]/@href').extract_first()),
            #    year=response.meta['year'],
            #    last_updated=datetime.now()
            #)
            yield course
