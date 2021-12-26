
from .faculty import Faculty
from .course import Course 
from .course_faculty import Course_Faculty 

import configparser as cp 
import os 

# Rename the files by the order it should be executed in the database. 
def rename_file(order: int, filename: str):
    path = "./data/sql"
    new_name = f"{path}/{order}_{filename}.sql"
    old_name = f"{path}/{filename}.sql"
    os.rename(old_name, new_name)

# Order that the files should be added to the database. 
order = ["faculty", "course", "course_faculty"]

config = cp.ConfigParser()
config.read("./configparser.ini")
faculty = Faculty(config).parse()
course = Course(config).parse()
course_faculty = Course_Faculty(config).parse() 

for i, filename in enumerate(order): 
    rename_file(i+1, filename)
