from .parser import Parser 
import configparser as cp

class Faculty(Parser):
    def __init__(self, config: cp.ConfigParser): 
        self.config = config 
        super().__init__("faculty", config['faculty']['csv'])

    def parse(self):
        cols_list = next(self.f_reader)
        cols = self.get_cols(cols_list)
        for faculty_id, row in enumerate(self.f_reader):   
            values = self.get_values(faculty_id, row)
            insert = self.sql_get_insert(cols, values)
            self.f_sql.write(insert)
