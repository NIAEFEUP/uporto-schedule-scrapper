.PHYONY: all clean 

all: scrapy 

scrapy:
	@-mkdir ./data/
	scrapy crawl faculties
	export YEAR=${YEAR}
	scrapy crawl courses
	scrapy crawl course_units -a user=${USER}
	scrapy crawl schedules -a user=${USER}

upload: 
	@echo [UPLOADING] files...
	@python scripts/upload.py

clean: 
	@echo [CLEANING] files from scrapper... 
	@-rm -r ./data/

