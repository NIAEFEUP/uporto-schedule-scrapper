.PHONY: all clean
FILES = $(shell ls)
        
# all: info faculties courses course_units course_metadata classes slots slot_professor professors
all: info faculties courses course_units course_metadata course_unit_group slots 

faculties: 
	scrapy crawl faculties 

courses: 
	scrapy crawl courses

course_units:
	scrapy crawl course_units

course_metadata:
	scrapy crawl course_metadata

course_unit_group:
	scrapy crawl course_unit_group

slots:
	scrapy crawl slots
	
info:
	python ./scrapper/info.py
	
class_vacancies:
	scrapy crawl class_vacancies
dump:
	@echo "Dumping files..."
	python ./scripts/dump.py
	@echo "Completed!"

upload:
	@echo "Uploading files..."
	@python ./scripts/upload.py
	@echo "Upload completed!"

convert_postgres:
	@echo "Converting dump to postgres..."
	@bash ./scripts/sqlite3-to-mysql.sh ./scripts/dump/data/dump_sqlite3.sql > ./scripts/dump/data/01_data.sql
	@echo "Convertion completed!"

clean: 
	@echo "Removing database.db"
	@rm ./scrapper/database/dbs/database.db
