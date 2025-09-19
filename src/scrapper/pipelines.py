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
        # Tracks how many items were processed until now.
        self.counter = 0
        # Avoids the percentage bar being initalized twice.
        self.pbar_initialized = False
        # If false, the percentage bar is not displayed.
        self.pbar_activated = eval(self.config['pbar']['activate'])

    def open_config(self):
        """
        Reads and saves the configuration file. 
        """
        config_file = "./config.ini"
        self.config = ConfigParser(interpolation=ExtendedInterpolation())
        self.config.read(config_file)

    def process_item(self, item, spider):
        self.process_pbar()
        self.db.insert(self.table_name, item)
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
        if not self.pbar_initialized:
            self.pbar = tqdm(total=self.expected_num)
            self.pbar_initialized = True

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
        if self.pbar_activated:
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
        self.table_name = 'faculty'

    def process_item(self, item, spider):
        if isinstance(item, items.Faculty):
            super().process_item(item, spider)
        return item


class CoursePipeline(MySQLPipeline):
    def __init__(self):
        MySQLPipeline.__init__(self)
        self.expected_num = int(self.config['statistics']['num_courses'])
        self.table_name = 'course'

    def process_item(self, item, spider):
        if isinstance(item, items.Course):
            super().process_item(item, spider)
        return item


class CourseUnitPipeline(MySQLPipeline):
    def __init__(self):
        MySQLPipeline.__init__(self)
        self.expected_num = int(self.config['statistics']['num_course_units'])
        self.table_name = 'course_unit'

    def process_item(self, item, spider):
        if isinstance(item, items.CourseUnit):
            super().process_item(item, spider)
        return item


class CourseMetadataPipeline(MySQLPipeline):
    def __init__(self):
        MySQLPipeline.__init__(self)
        self.expected_num = int(
            self.config['statistics']['num_course_metadata'])
        self.table_name = 'course_metadata'

    def process_item(self, item, spider):
        if isinstance(item, items.CourseMetadata):
            super().process_item(item, spider)
        return item


class ClassPipeline(MySQLPipeline):
    def __init__(self):
        MySQLPipeline.__init__(self)
        self.expected_num = int(self.config['statistics']['num_classes'])
        self.table_name = 'class'

    def process_item(self, item, spider):
        if isinstance(item, items.Class):
            super().process_item(item, spider)
        return item


class SlotPipeline(MySQLPipeline):
    def __init__(self):
        MySQLPipeline.__init__(self)
        self.expected_num = int(self.config['statistics']['num_slots'])
        self.table_name = 'slot'

    def process_item(self, item, spider):
        if isinstance(item, items.Slot):
            super().process_item(item, spider)
        return item


class SlotClassPipeline(MySQLPipeline):
    def __init__(self):
        MySQLPipeline.__init__(self)
        self.expected_num = int(self.config['statistics']['num_slot_class'])
        self.table_name = 'slot_class'

    def process_item(self, item, spider):
        if isinstance(item, items.SlotClass):
            super().process_item(item, spider)
        return item


class SlotProfessorPipeline(MySQLPipeline):
    def __init__(self):
        MySQLPipeline.__init__(self)
        self.expected_num = int(
            self.config['statistics']['num_slot_professor'])
        self.table_name = 'slot_professor'

    def process_item(self, item, spider):
        if isinstance(item, items.SlotProfessor):
            super().process_item(item, spider)
        return item


class ProfessorsPipeline(MySQLPipeline):
    def __init__(self):
        MySQLPipeline.__init__(self)
        self.expected_num = int(self.config['statistics']['num_professors'])
        self.table_name = 'professor'

    def process_item(self, item, spider):
        if isinstance(item, items.Professor):
            super().process_item(item, spider)
        return item

class CourseGroupPipeline(MySQLPipeline):
    def __init__(self):
        MySQLPipeline.__init__(self)
        self.expected_num = int(self.config['statistics']['num_course_groups'])
        self.table_name = 'course_group'

    def process_item(self, item, spider):
        if isinstance(item, items.CourseGroup):
            print("CG PROCESS")
            super().process_item(item, spider)
        return item


class CourseUnitGroupPipeline(MySQLPipeline):
    def __init__(self):
        MySQLPipeline.__init__(self)
        self.expected_num = int(self.config['statistics']['num_course_unit_course_group'])
        self.table_name = 'course_unit_course_group'

    def process_item(self, item, spider):
        if isinstance(item, items.CourseUnitGroup):
            print("CourseUnitGroup PROCESS")
            super().process_item(item, spider)
        return item



class CoursePathPipeline(MySQLPipeline):
    def __init__(self):
        MySQLPipeline.__init__(self)
        self.expected_num = int(
            self.config['statistics']['num_course_path'])
        self.table_name = 'course_path'

    def process_item(self, item, spider):
        if isinstance(item, items.CoursePath):
            super().process_item(item, spider)
        return item