
from .faculty import Faculty
from .course import Course 
from .course_faculty import Course_Faculty 

import configparser as cp 

config = cp.ConfigParser()
config.read("./configparser.ini")
faculty = Faculty(config).parse()
course = Course(config).parse()
course_faculty = Course_Faculty(config).parse()