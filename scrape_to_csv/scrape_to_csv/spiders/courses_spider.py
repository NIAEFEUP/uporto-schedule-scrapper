import scrapy
import csv
from operator import itemgetter
from urllib.parse import urlparse, parse_qs

FACULTIES_CSV_FILE_PATH = "output2/faculties.csv"

class CoursesSpider(scrapy.Spider):
    name = "courses"
    allowed_domains = ["sigarra.up.pt"]

    raw_courses_url = "https://sigarra.up.pt/{faculty}/pt/cur_geral.cur_tipo_curso_view?pv_tipo_sigla={course_type}&pv_ano_lectivo={school_year}"


    def start_requests(self):
        # TODO: Get from arguments, env variables, etc, somewhere
        year = 2021

        faculties = []

        with open(FACULTIES_CSV_FILE_PATH, "r") as f:
            csv_data = csv.DictReader(f)
            faculties = [faculty["acronym"] for faculty in csv_data]

        COURSE_TYPES = ['L', 'M', 'MI', 'D']

        for faculty in faculties:
            for course_type in COURSE_TYPES:
                url = self.raw_courses_url.format(faculty=faculty, course_type=course_type, school_year=year)
                # self.logger.debug(f"Calculated url: {url}")
                meta_data = {"faculty_acronym": faculty, "course_type": course_type, "year": year}

                yield scrapy.Request(url=url, callback=self.parse_course_list, meta=meta_data)

    def parse_course_list(self, response):
        """
        Parses the initial course list page.
        Then, issues follow-up requests to the course pages themselves to get more information.
        `response.follow_all` is used since the `href`s are relative links, and the relevant elements are <a>s
        """

        # Get the <ul> whose preceding sibling is an <h2> with the text "Lista de Cursos"
        ul = response.xpath("//ul[preceding-sibling::h2[text()='Lista de Cursos']]")
        # Then, get the children elements (<li>s) and their respective first <a>
        # These have the course information (following <a>s just mention if the course is a collaboration between faculties, etc. - not relevant for this)
        courses = ul.xpath("./li/a[1]")

        # `courses` is a set of <a>s so we can use the shorter `response.follow_all` instead of `response.follow`
        # also forward the response.meta data
        yield from response.follow_all(courses, meta=response.meta, callback=self.parse_course)

            
    def parse_course(self, response):
        """
        Parses a specific course page.
        The url should look something like: `https://sigarra.up.pt/feup/pt/cur_geral.cur_view?pv_ano_lectivo={school_year}&pv_origem=CUR&pv_tipo_cur_sigla={course_type}&pv_curso_id={course_id}`
        Direct navigation can't be used since the course_id is not known beforehand.
        """

        # Checks if the course page is pointing elsewhere (see details below)
        # Previous selector was response.css("body").xpath("//*[@id='conteudoinner']/div[1]/a").get()
        # This was a true positive for https://sigarra.up.pt/fcup/pt/cur_geral.cur_view?pv_ano_lectivo=2021&pv_origem=CUR&pv_tipo_cur_sigla=D&pv_curso_id=21901
        # But a false positive for https://sigarra.up.pt/faup/pt/cur_geral.cur_view?pv_ano_lectivo=2021&pv_origem=CUR&pv_tipo_cur_sigla=D&pv_curso_id=45
        # TODO: Decide if we just ignore the specific page (the one that points to another) since the data would be duplicate; if we scrape the page since the data is hidden but still there, or if we try to follow the link
        # TODO: Regardless of the above, we have to find a selector that works for one but not the other. Just checking "first div child of div#conteudoinner that has a <a>" will work for both...
        #TODO: Check if the "test if this page points to another one" is necessary...

        courseHtml = response.css("body")
        if courseHtml.xpath("//*[@id='conteudoinner']/div[1]/a").get() is not None:
            parsed_url = urlparse(response.url)
            queryparams = parse_qs(parsed_url.query)
            course_id = queryparams['pv_curso_id'][0]
            self.logger.warn("Found a possible pointer to another page for course with id={} at {} (url is {})".format(course_id, response.meta["faculty_acronym"], response.url))
        # end this check

        # Get the data forwarded using response.meta
        faculty_acronym, course_type, school_year = itemgetter("faculty_acronym", "course_type", "year")(response.meta)

        # Get course_id from the URL
        # See https://stackoverflow.com/questions/5074803
        parsed_url = urlparse(response.url)
        queryparams = parse_qs(parsed_url.query)
        course_id = queryparams['pv_curso_id'][0]

        # In the "Planos de Estudos" section, get the first link in the div box
        relative_plan_url = response.xpath("//h3[contains(., 'Planos de Estudos')]/following-sibling::div[1]//a[1]/@href").get()

        yield {
                "id": course_id,
                "name": response.xpath("//h1[2]/text()").get(), # Second h1 in page
                "type": course_type,
                "acronym": response.xpath("//td[preceding-sibling::td[contains(., 'Sigla:')]]/text()").get(),
                "url": response.url, # not sure how this is useful
                "plan_url": response.urljoin(relative_plan_url),

                "faculty": faculty_acronym,
                "year": school_year,
        }
