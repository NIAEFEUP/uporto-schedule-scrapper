# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from . import items
from configparser import ConfigParser, ExtendedInterpolation
from .database.Database import Database
from tqdm import tqdm


class MySQLPipeline():
    def __init__(self): 
        self.open_config()
        self.db = Database()
        self.counter = 0        # Tracks how many items were processed until now.
        self.pbar_activated = False

    def open_config(self):
        """
        Reads and saves the configuration file. 
        """
        config_file = "./config.ini"
        self.config = ConfigParser(interpolation=ExtendedInterpolation())
        self.config.read(config_file)

    def process_item(self, item, spider):
        return item 

    # -------------------------------------------------------------------------
    # Percentage bar
    # -------------------------------------------------------------------------


    def config_pbar(self):
        """
        Configures the porcentage bar and makes it visible. 
        The total number of elements is based on previous interactions. 
        Thus the 100% might not always mean that the program has enterily finished, 
        but it's actually really close to that. 
        """
        if not self.pbar_activated:
            self.pbar = tqdm(total=self.expected_num)
            self.pbar_activated = True 

    def update_pbar(self):
        """
        Update the percentage bar by one.
        """
        self.pbar.update(1)

    def close_pbar(self): 
        """
        Closes the percentage bar once if reaches to 100%. 
        """
        if self.counter == self.expected_num:
            self.pbar.close()
    
    def process_pbar(self):
        """
        This function configures the percentage bar if necessary,
        update the counter, update and close (if necessary) the percentage bar. 
        This the cycle a percentage bar in every pipeline. 
        """
        if eval(self.config['pbar']['activate']):
            self.config_pbar()
            self.counter += 1
            self.update_pbar()
            self.close_pbar()

# -------------------------------------------------------------------------
# Pipelines
# -------------------------------------------------------------------------

class FacultyPipeline(MySQLPipeline):
    def __init__(self):
        MySQLPipeline.__init__(self)
        self.expected_num = int(self.config['statistics']['num_faculties'])

    def process_item(self, item, spider):
        if isinstance(item, items.Faculty):
            self.process_pbar()
            self.db.insert('faculty', item)
        return item 



class CoursePipeline(MySQLPipeline):
    def __init__(self):
        MySQLPipeline.__init__(self)
        self.expected_num = int(self.config['statistics']['num_courses'])

    def process_item(self, item, spider):
        if isinstance(item, items.Course):
            self.process_pbar()
            self.db.insert_course('course', item)
        return item 

class CourseUnitPipeline(MySQLPipeline):
    def __init__(self):
        MySQLPipeline.__init__(self)
        self.expected_num = int(self.config['statistics']['num_course_units'])

    def process_item(self, item, spider):
        if isinstance(item, items.CourseUnit):
            self.process_pbar()
            self.db.insert()
        return item


class SchedulePipeline(MySQLPipeline):
    def __init__(self):
        MySQLPipeline.__init__(self)
        self.expected_num = int(self.config['statistics']['num_schedules'])

    def process_item(self, item, spider):
        if isinstance(item, items.Schedule):
            self.process_pbar()
            self.db.insert_schedule(list(item.values()))
        return item
     