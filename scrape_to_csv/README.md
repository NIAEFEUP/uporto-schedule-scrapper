# Scraper to CSV

This scraper is built using [Scrapy](https://scrapy.org/) ([docs](https://docs.scrapy.org/en/latest/intro/overview.html)).

Its purpose is to scrape relevant entities into CSV files, which may then be used to populate a database.

The extracted entities are:
* Faculties (all of UPorto's faculties)
* Courses (the courses that are active in a certain year for all of the found faculties)
* CourseUnits (aka _"cadeiras"_)
* Schedule "items" for each CourseUnit

## Setup and installation

The scraper is Dockerized so either the provided Dockerfile or the `docker-compose.yml` at the root of the project can be used.

If a local installation is preferred, just `pip install -r requirements.txt`.  
**Note:** Usage of a python virtual environment is _highly_ recommended for a local setup.

## Usage

There is a spider that crawls pages and extracts each of the above entities.

To run a spider, just run `scrapy crawl <spider_name>`. For example, `scrapy crawl faculties` will crawl SIGARRA and extract all of the faculties.

**(The following part may change in the future)**

So that the scraping results are stored in a CSV file, run the spiders with the `-O` option.  
For example, `scrapy crawl faculties -O output/faculties.csv` will run the faculties scraper and output the scraped data into the `faculties.csv` file in the `output` directory (relative to the project root).

**(May change)** The scrapers assume that the files of the previous scrapings are placed in the `output/` directory. For example, to run the Course spider, `output/faculties.csv` should exist and be populated with the faculties via the faculties scraper.

## Notes of specific behaviours or issues

* Courses that are hosted by several faculties ("co-op" courses) have "duplicate" lines in the courses CSV. This may be necessary since the `plan_url` is different. However, these should probably be "deduplicated" by the module that populates the DB from the CSVs, joining the several "instances" of the same course in different faculties.
    * The desired behaviour should be something like: Being able to find the course from either of the associated faculties; and also being able to see all of the associated course units, regardless of these being present in either "instance" of the course. This way the information will be as connected as possible :)
    * Note that this may also generate some duplication in the following steps, which may require additional care in implementing the module that populates the database from the CSV file.
