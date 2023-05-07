import sqlite3
from configparser import ConfigParser, ExtendedInterpolation


class Dump: 

    def __init__(self):
        self.open_config() 

    def open_config(self):
        """
        Reads and saves the configuration file. 
        """
        config_file = "./config.ini"
        self.config = ConfigParser(interpolation=ExtendedInterpolation())
        self.config.read(config_file)

    def get_dump_filepath(self): 
        file_path = self.config['dump']['path']
        dump_filename = self.config['dump']['filename']
        return "{0}/{1}".format(file_path, dump_filename)

    def get_db_filepath(self): 
        file_path = self.config['database']['path']
        filename = self.config['database']['filename']
        return "{0}/{1}".format(file_path, filename)


    def dump(self): 
        dump_filepath = self.get_dump_filepath()
        db_filepath = self.get_db_filepath()
        con = sqlite3.connect(db_filepath)
        f = open(dump_filepath, 'w', encoding="utf-8")
        self.dump_table("faculty", con, f)
        self.dump_table("course", con, f)
        self.dump_table("course_unit", con, f)
        self.dump_table("course_metadata", con, f)
        self.dump_table("professor", con, f)
        self.dump_table("schedule", con, f)
        self.dump_table("schedule_professor", con, f)
        f.close()

    def dump_table(self, table, con, f): 
        for line in con.iterdump():
            if line.startswith("INSERT") and "\"{}\"".format(table) in line:
                f.write('%s\n' % line)


if __name__ == '__main__': 
    dump = Dump()
    dump.dump()
