from re import A
from .parser import Parser 
import configparser as cp

class Course(Parser):
    def __init__(self, config: cp.ConfigParser):
        self.config = config
        super().__init__("course", config['course']['csv'])
    
    def parse(self):   
        cols_list = next(self.f_reader)   

        # Get faculties index. 
        faculties_col_name = self.config['course']['faculties_col']
        faculties_index = cols_list.index(faculties_col_name) 

        # Drop faculties col. 
        del cols_list[faculties_index]
        cols = self.get_cols()  

        # Generate inserts 
        for course_id, row in enumerate(self.f_reader): 
            del row[faculties_index]    # Remove faculties position.
            values = self.get_values(course_id, row)
            insert = self.sql_get_insert(cols, values) 
            self.f_sql.write(insert)




        
