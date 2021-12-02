
from .faculty import Faculty
from .course import Course
import configparser as cp 

config = cp.ConfigParser()
config.read("./configparser.ini")
faculty = Faculty(config).parse()
course = Course(config).parse()