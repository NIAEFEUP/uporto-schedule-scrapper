# University of Porto Timetable Scraper - *UPTS*
Python solution to extract the courses schedules from the different Faculties of Univerty of Porto.

## Requirements
- [Python 3](https://www.python.org)
- [Scrapy](https://scrapy.org)
- [VirtualEnv (optional but recommended)](http://python-guide-pt-br.readthedocs.io/en/latest/dev/virtualenvs/)

Not tested but answer or postpone the pedagogical surveys.

## Usage
Run the following scrapy command. Make sure you have all the requirements.
```
scrapy crawl login_feup -a user=«USERCODE» -a passw=«PASSWORD»
```
Where `«USERCODE»` is your up account username and `«PASSWORD»` its password.
The output will be exported to an entire JSON file called `classe.js`.

## Developing
UPTS follows a standard scrapy program template with the final output beign the item `FinalSchedule` defined in items.py it is composed by the following `Scrapy Fields`:
* **course**
* **date**
* **title**
* **text**
* **duration**
* **acronym**
* **professor**
* **prof_acro**
* **id_class**
* **location**

These items will be passed to the item pipeline which will write them to a JSON file, in the future it will be a MySQL database. It's written in the pipelines.py.

#### To Implement
- [x] Refactor, Clean code and comments.
- [x] Follow a scrapy template.
- [x] Use items and item pipelines.
- [ ] Implement Weekday field.
- [ ] Export items to a MySql database.
- [ ] Finish Faculdade scrapper.
- [ ] Document Faculdade scrapper.
