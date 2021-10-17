# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html
from dataclasses import dataclass, field
from typing import Optional

# Based on the previous items.py, adaptation may be necessary

@dataclass
class Faculty:
    acronym: str
    name: str

@dataclass
class Course:
    # Cannot use id and type because they are keywords in python
    course_id: int
    name: str
    course_type: str
    acronym: str
    url: str # Not sure that this is useful
    plan_url: str
    faculty: str
    year: int

@dataclass
class CourseUnit:
    course_unit_id: int
    name: str
    acronym: str
    course_id: int
    url: str
    year: int
    schedule_url: str

@dataclass
class Schedule:
    course_unit_id: int
    lesson_type: str # T, TP, PL, etc.
    day: int # 0 = monday, 1 = tuesday, .., 5 = saturday (no sunday)
    duration: float # In hours. 0.5 hours is half an hour
    start_time: int # TODO: Confirm data type
    teacher_acronym: str # JAS, GTD, etc.
    location: str # room name/number
    class_name: str # 1MIEIC01
    composed_class_name: Optional[str] = field(default=None) # None or COMP_372 # TODO: See if this can be joined with the previous if it makes sense to do so
