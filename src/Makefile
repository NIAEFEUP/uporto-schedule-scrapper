.PHONY: all clean

all: faculties courses course_units schedules

faculties: 
	scrapy crawl faculties 

courses: 
	scrapy crawl courses

course_units:
	scrapy crawl course_units -a user=up201800175

schedules:
	scrapy crawl schedules -a user=up201800175

clean: 
	@echo "Removing database.db"
	@rm ./scrapper/database/dbs/database.db