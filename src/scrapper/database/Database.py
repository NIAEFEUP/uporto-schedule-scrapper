import sqlite3 
import psycopg2
from os.path import exists
from configparser import ConfigParser, ExtendedInterpolation

from dotenv import dotenv_values

import os

CONFIG = {
    **dotenv_values(".env"),  # load variables
    **os.environ,  # override loaded values with environment variables
}

class Database:    
    # -------------------------------------------------------------------------
    # Creation
    # -------------------------------------------------------------------------

    def __init__(self): 
        try: 
            self.open_config()
            self.database_file_path = self.get_database_path()

            exists_db = exists(self.database_file_path) 

            self.connection = sqlite3.connect(self.database_file_path, check_same_thread=False, isolation_level=None) if int(CONFIG['PROD']) == 0 else psycopg2.connect(
                host=CONFIG['POSTGRES_HOST'],
                port=CONFIG['POSTGRES_PORT'],
                user=CONFIG['POSTGRES_USER'],
                password=CONFIG['POSTGRES_PASSWORD'],
                dbname=CONFIG['POSTGRES_DB']
            )

            self.cursor = self.connection.cursor()

            if not exists_db:
                self.create_table()

        except Exception as e:
            print("[ERR] - INIT DB :: ?", e)

    # -------------------------------------------------------------------------
    # Configurations
    # ------------------------------------------------------------------------- 

    def open_config(self):
        """
        Reads and saves the configuration file. 
        """
        config_file = "./config.ini"
        self.config = ConfigParser(interpolation=ExtendedInterpolation())
        self.config.read(config_file)

    def get_database_path(self): 
        path = self.config['database']['path']
        filename = self.config['database']['filename']
        return "{0}/{1}".format(path, filename) 

    def create_table(self): 
        try: 
            sql_script = open("./scrapper/database/dbs/create_db_sqlite3.sql").read()
            sql_commands = sql_script.split(";"); 
            for command in sql_commands:
                self.cursor.execute(command)    
                self.connection.commit()     
        except Exception as e: 
            print("[ERR] - CREATE DB :: ?", e) 

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

    def insert(self, table_name, item): 
        try:
            sql = "INSERT INTO `{0}` (`{1}`) VALUES ({2})"
            columns = "`, `".join(item.keys())
            values = ", ".join("?" for _ in item.values())
            prepare = sql.format(table_name, columns, values)
            self.execute(prepare, list(item.values()))
        except sqlite3.Error as e: 
            print("[ERR] - INSERT {} :: {}".format(table_name.upper(), e))

 
            
    # -------------------------------------------------------------------------
    # Get functions
    # ------------------------------------------------------------------------- 
