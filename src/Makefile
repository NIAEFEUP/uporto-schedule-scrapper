.PHONY: all clean

all: faculties courses course_units schedules

faculties: 
	scrapy crawl faculties 

courses: 
	scrapy crawl courses

course_units:
	scrapy crawl course_units

schedules:
	scrapy crawl schedules

clean: 
	@echo "Removing database.db"
	@rm ./scrapper/database/dbs/database.db