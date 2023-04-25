.PHONY: all clean

all: faculties courses course_units course_metadata schedules schedule_professor professors


faculties: 
	scrapy crawl faculties 

courses: 
	scrapy crawl courses

course_units:
	scrapy crawl course_units

course_metadata:
	scrapy crawl course_metadata
	
schedules:
	scrapy crawl schedules

schedule_professor:
	scrapy crawl schedule_professor

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