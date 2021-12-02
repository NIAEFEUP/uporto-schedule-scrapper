import csv
from utils import paths, utils

TABLE_NAME = "faculties"

# Reading files
f = open(paths.get_input_filepath(TABLE_NAME) , "r") 
f_sql = open(paths.get_output_filepath(TABLE_NAME), "w")
f_reader = csv.reader(f)


col_names = ','.join(list(map(utils.add_brackets_cols, ['id'] + next(f_reader))))    # Names for each column   

for faculty_id, row in enumerate(f_reader):  
    values = ','.join([str(faculty_id)] + list(map(utils.add_brackets_vals, row)))
    f_sql.write(f"INSERT INTO `faculty`({col_names}) VALUES ({values});\n") 
