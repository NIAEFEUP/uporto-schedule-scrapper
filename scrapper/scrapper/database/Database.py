import sqlite3 
from os.path import exists

class Database:
    def __init__(self): 
        print("here")
        try: 
            self.database_file_path = "./scrapper/database/dbs/database.db"
            exists_db = exists(self.database_file_path) 
            self.connection = sqlite3.connect(self.database_file_path, check_same_thread=False, isolation_level=None)
            self.cursor = self.connection.cursor()

            if not exists_db:
                self.create_table()

        except Exception as e:
            print("EXCEPTION")
            print(e)

    def create_table(self): 
        try: 
            sql_script = open("./scrapper/database/dbs/create_db_sqlite3.sql").read()
            sql_commands = sql_script.split(";"); 
            for command in sql_commands:
                print(command)
                self.cursor.execute(command)
                self.connection.commit()     
        except Exception as e: 
            print("EXCEPTION HERE")
            print(e)



