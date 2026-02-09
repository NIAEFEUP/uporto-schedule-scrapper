#!/usr/bin/env python3

import sqlite3
from configparser import ConfigParser, ExtendedInterpolation
from typing import TextIO

CONFIG_PATH = './config.ini'

def get_config():
    config = ConfigParser(interpolation=ExtendedInterpolation())
    config.read(CONFIG_PATH)
    return config

def get_db_connection(config: list[str]):
    path = config['database']['path']
    filename = config['database']['filename']
    filepath = path + '/' + filename

    return sqlite3.connect(filepath)

def get_dump_filepath(config: list[str]):
    path = config['vacancies_dump']['path']
    filename = config['vacancies_dump']['filename']
    filepath = path + '/' + filename

    return filepath

def dump_class_vacancies(course_unit_id: int, name: str, vacancies: int, dump_file: TextIO):
    stmt = "UPDATE class SET vacancies = {} WHERE course_unit_id = {} AND name = '{}';" \
        .format(vacancies, course_unit_id, name)
    dump_file.write(stmt + "\n")

def dump_vacancies():
    config = get_config()
    db_conn = get_db_connection(config)
    dump_filepath = get_dump_filepath(config)

    with open(dump_filepath, 'w', encoding='utf-8') as dump_file:
        cursor = db_conn.cursor()
        cursor.execute("""
            SELECT course_unit_id, name, vacancies
            FROM class
        """)

        for course_unit_id, name, vacancies in cursor.fetchall():
            dump_class_vacancies(course_unit_id, name, vacancies, dump_file)

if __name__ == '__main__':
    dump_vacancies()