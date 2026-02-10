#!/usr/bin/env python3
import sqlite3
import psycopg2
from configparser import ConfigParser, ExtendedInterpolation

import os
from dotenv import dotenv_values

from typing import Optional, TextIO

CONFIG = {
    **dotenv_values(".env"),  # load variables
    **os.environ,  # override loaded values with environment variables
}

CONFIG_PATH = './config.ini'

def get_config():
    config = ConfigParser(interpolation=ExtendedInterpolation())
    config.read(CONFIG_PATH)
    return config

def get_db_connection(config: ConfigParser):
    print("Using SQLite database")
    path = config['database']['path']
    filename = config['database']['filename']
    filepath = path + '/' + filename

    return sqlite3.connect(filepath)

def get_db_connection_postgres(config: ConfigParser):
    print("Using PostgreSQL database")

    host = CONFIG['POSTGRES_HOST']
    port = CONFIG['POSTGRES_PORT']
    user = CONFIG['POSTGRES_USER']
    password = CONFIG['POSTGRES_PASSWORD']
    dbname = CONFIG['POSTGRES_DB']

    return psycopg2.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        dbname=dbname
    )

def get_dump_filepath(config: ConfigParser):
    path = config['vacancies_dump']['path']
    filename = config['vacancies_dump']['filename']
    filepath = path + '/' + filename

    return filepath

def dump_class_vacancies(course_unit_id: int, name: str, vacancies: Optional[int], dump_file: TextIO):
    if vacancies is None:  # Ignore classes with no vacancies information
        return

    escaped_name = name.replace("'", "''")
    stmt = "UPDATE class SET vacancies = {} WHERE course_unit_id = {} AND name = '{}';" \
        .format(vacancies, course_unit_id, escaped_name)
    dump_file.write(stmt + "\n")

def dump_vacancies():
    config = get_config()
    dump_filepath = get_dump_filepath(config)

    with open(dump_filepath, 'w', encoding='utf-8') as dump_file:
        prod = CONFIG['PROD'] if CONFIG['PROD'] is not None else 0
        connection = get_db_connection(config) if int(prod) == 0 else get_db_connection_postgres(config)
        with connection as db_conn:
            cursor = db_conn.cursor()
            cursor.execute("""
                SELECT course_unit_id, name, vacancies
                FROM class
            """)

            for course_unit_id, name, vacancies in cursor.fetchall():
                dump_class_vacancies(course_unit_id, name, vacancies, dump_file)

if __name__ == '__main__':
    dump_vacancies()