.PHONY: all clean

all: faculties courses course_units schedules professors

faculties: 
	scrapy crawl faculties 

courses: 
	scrapy crawl courses

course_units:
	scrapy crawl course_units

course_units_year:
	scrapy crawl course_units_year
	
schedules:
	scrapy crawl schedules

professors:
	scrapy crawl professors

dump:
	@echo "Dumping files..."
	python ./scripts/dump.py
	@echo "Completed!"

upload:
	@echo "Uploading files..."
	@python ./scripts/upload.py
	@echo "Upload completed!"

convert_mysql:
	@echo "Converting dump to mysql..."
	@bash ./scripts/sqlite3-to-mysql.sh ./scripts/dump/data/dump_sqlite3.sql > ./scripts/dump/data/dump_mysql.sql
	@echo "Convertion completed!"

clean: 
	@echo "Removing database.db"
	@rm ./scrapper/database/dbs/database.db