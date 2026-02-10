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

The default logging level is `WARNING`. To change this, use the `--loglevel` or `-L` option with the desired level (e.g. `DEBUG`, `INFO`).

A feed export is configured in the scrapy project configs so that each spider outputs its data to `output/spidername.csv`.

The spiders assume that the files of previous stages of the scraper are present in this file and directory structure. For example, to be able to run the Course spider, `output/faculties.csv` should exist and be populated with faculties (result of simply running the faculty crawler).

As such, to get the full scraping output, one simply needs to run:
```
scrapy crawl faculties
scrapy crawl courses
scrapy crawl courseunits ?
scrapy crawl schedules
```

TODO: Possibly implement something with https://doc.scrapy.org/en/stable/topics/practices.html#run-scrapy-from-a-script -> this would simply the crawling process by just having one script be ran and everything else would "just work" TM

## Notes of specific behaviours or issues

* Courses that are hosted by several faculties ("co-op" courses) have "duplicate" lines in the courses CSV. This may be necessary since the `plan_url` is different. However, these should probably be "deduplicated" by the module that populates the DB from the CSVs, joining the several "instances" of the same course in different faculties.
    * The desired behaviour should be something like: Being able to find the course from either of the associated faculties; and also being able to see all of the associated course units, regardless of these being present in either "instance" of the course. This way the information will be as connected as possible :)
    * Note that this may also generate some duplication in the following steps, which may require additional care in implementing the module that populates the database from the CSV file.

* A course's plan only requires the year (`pv_ano_lectivo`) and the study plan ID (`pv_plano_id`). It also does not seem to matter which faculty is fetched (i.e. replacing `feup` with `fcup` in the URL to get the course plan does not change the resulting data).
    * This may be helpful in de-duplicating data, since we need only to map a course id (`pv_curso_id`) to a course plan id (`pv_plano_id`) to get the full list of course units.
    * Hopefully this consideration will help in reducing the number of requests that are made to get all of the course units, and thus the duration necessary for scraping.
    * However, this may be temporary behaviour which may be changed in the future, since the same does not happen with courses... If a course is lectured at FEUP, changing the url to FAUP breaks the page with an error.
    * Still, for now it seems like a better option to simply consider the plan id as a set, to reduce duplication.
