from abc import abstractclassmethod
import os 
import csv 

class Parser: 
    def __init__(self, table_name: str, csv_name: str = None):
        self.current_path = os.path.dirname(os.path.abspath(__file__))    
        self.table_name = table_name
        self.csv_name = csv_name 

        # Creating sql.
        self.f_sql = open(self.get_output_filepath(), "w")    

        # Reading csv. 
        if csv_name is not None: 
            f = open(self.get_input_filepath() , "r")  
            self.f_reader = csv.reader(f) 

    
    def add_brackets_vals(self, x: str):
        return f"'{x}'"  

    def add_brackets_cols(self, x: str):  
        return f"`{x}`" 

    def sql_get_insert(self, cols: list, values: list): 
        return f"INSERT INTO {self.table_name} ({cols}) VALUES ({values}); \n"

    def get_input_filepath(self, csv_name=None): 
        if csv_name is None:
            return f"{self.current_path}/../data/raw/{self.csv_name}.csv" 
        return f"{self.current_path}/../data/raw/{csv_name}.csv" 

    def get_output_filepath(self):
        return f"{self.current_path}/../data/sql/{self.table_name}.sql"

    def get_cols(self, cols_list, with_id=True):  
        if with_id:
            return ','.join(list(map(self.add_brackets_cols, ['id'] + cols_list)))     
        return ','.join(list(map(self.add_brackets_cols, cols_list)))     

    def get_values(self, id_, row, with_id=True): 
        if with_id:
            return ','.join([str(id_)] + list(map(self.add_brackets_vals, row)))     
        return ','.join(list(map(self.add_brackets_vals, row)))     


    @abstractclassmethod 
    def parser(self):
        pass 