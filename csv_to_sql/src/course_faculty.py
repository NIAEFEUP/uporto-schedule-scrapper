import configparser as cp
from .parser import Parser 
import pandas as pd 
from ast import literal_eval 

class Course_Faculty(Parser):
    def __init__(self, config: cp.ConfigParser): 
        self.config = config
        super().__init__("course_faculty", None) 
        self.df_faculty = pd.read_csv(self.get_input_filepath(config['faculty']['csv']), index_col=False) 
        self.df_course = pd.read_csv(self.get_input_filepath(config['course']['csv']), index_col=False)  

    def get_faculty_id(self, faculty_acronym: str): 
        return self.df_faculty[self.df_faculty['acronym'] == faculty_acronym].index[0]


    def parse(self):  
        cols = self.get_cols(["course_id", "faculty_id"], with_id=False)   

        # Get faculties index. 
        faculties_col_name = self.config['course']['faculties_col'] 
        
        # For each course get's the faculties ids that it's associated. 
        for course_id, faculties in enumerate(self.df_course[faculties_col_name]):     
            # Acronym to id 
            faculties_acronyms = literal_eval(faculties)
            faculties_ids = list(map(self.get_faculty_id, faculties_acronyms))     
            # For each id create on instance in the table
            for faculty_id in faculties_ids:   
                values = self.get_values(None, [course_id, faculty_id], with_id=False)
                insert = self.sql_get_insert(cols, values)
                self.f_sql.write(insert)

