# University of Porto Timetable Scraper
Python solution to extract the courses schedules from the different Faculties of Univerty of Porto.

## Requirements
- [Python 3](https://www.python.org)
- [Scrapy](https://scrapy.org)
- [VirtualEnv (optional but recommended)](http://python-guide-pt-br.readthedocs.io/en/latest/dev/virtualenvs/)

Not tested but answer or postpone the pedagogical surveys.

## Usage
Run the `sigarra_scraper.py` file with python. Make sure you have all the requirements.
```
python sigarra_scraper.py
```

## Developing
Included there is a file 'hor_21.html' intended for training/testing the extraction of class information.
It is intended to be used with the scrapy shell with a terminal open on same folder as file.

'scrapy shell ./hor_21.html'

The file is loaded as response. Use response.xpath('«XPATH QUERRY»') to select things.