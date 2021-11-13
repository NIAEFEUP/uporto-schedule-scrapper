import os 
CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))

def get_input_filepath(table_name: str):
    return f"{CURRENT_PATH}/../data/raw/{table_name}.csv"

def get_output_filepath(table_name: str):
    return f"{CURRENT_PATH}/../data/sql/{table_name}.sql"


