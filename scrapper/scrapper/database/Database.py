import sqlite3 
from os.path import exists

class Database:    
    # -------------------------------------------------------------------------
    # Creation
    # -------------------------------------------------------------------------

    def __init__(self): 
        try: 
            self.database_file_path = "./scrapper/database/dbs/database.db"
            exists_db = exists(self.database_file_path) 
            self.connection = sqlite3.connect(self.database_file_path, check_same_thread=False, isolation_level=None)
            self.cursor = self.connection.cursor()

            if not exists_db:
                self.create_table()

        except Exception as e:
            print("[ERR] - INIT DB :: %s", e)

    def create_table(self): 
        try: 
            sql_script = open("./scrapper/database/dbs/create_db_sqlite3.sql").read()
            sql_commands = sql_script.split(";"); 
            for command in sql_commands:
                self.cursor.execute(command)    
                self.connection.commit()     
        except Exception as e: 
            print("[ERR] - CREATE DB :: %s", e) 

    # -------------------------------------------------------------------------
    # SQL interaction
    # ------------------------------------------------------------------------- 

    def execute(self, command, arguments=None):
        if arguments is None:
            self.cursor.execute(command)
        else:
            self.cursor.execute(command, arguments)
        self.connection.commit()


    # -------------------------------------------------------------------------
    # Insert functions
    # -------------------------------------------------------------------------

    def insert_faculty(self, values): 
        try: 
            self.execute("""
                INSERT INTO `faculty` (`acronym`, `name`, `last_updated`) 
                VALUES(?,?,?)
            """, values)
        except sqlite3.Error as e:
            print("[ERR] - INSERT FACULTY :: %s", e)



