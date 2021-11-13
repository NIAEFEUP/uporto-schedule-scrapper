import csv
import os
from parser.utils import mysql 
from utils import mysql, paths

TABLE_NAME = "faculties"

# Reading files
f = open(paths.get_input_filepath(TABLE_NAME) , "r")
f_sql = open(paths.get_output_filepath(TABLE_NAME), "w")
f_reader = csv.reader(f)

# Type 
head = next(f_reader, None)
types = ["VARCHAR(20)", "VARCHAR(100)"]
f_sql.write(mysql.get_create_table(TABLE_NAME, head, types))



