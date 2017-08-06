# University of Porto Timetable Scraper
Python solution to extract the courses schedules from the different Faculties of Univerty of Porto.

## Requirements
- [Python 3](https://www.python.org)
- [Scrapy](https://scrapy.org)
- [VirtualEnv (optional but recommended)](http://python-guide-pt-br.readthedocs.io/en/latest/dev/virtualenvs/)
- [UnQLite and unqlite-python](https://unqlite-python.readthedocs.io/en/latest/installation.html)

Not tested but answer or postpone the pedagogical surveys.

## Usage
Run the `sigarra_scraper.py` file with python. Make sure you have all the requirements.
```
python sigarra_scraper.py
```
After installing the UnQLite and unqlite-python and running the previous command a database on the same folder called
class.db will be generated, to open it go to a python shell (or in a python script) and type these commands:
```
>>> from unqlite import UnQLite
>>> db = UnQLite('./class.db') #or path to class.db
>>> classes = db.collection('classes')
>>> classes.exists()
>>> classes.all() #will return every record on db
```

To querry the db read the [api documentation](https://unqlite-python.readthedocs.io/en/latest/quickstart.html), the function
that will be used will be the filter() applied to the collection. To use this pass a lambda function that takes one parameter
and returns a boolean to the filter() function.

```
>>>classes.filter(lambda obj : obj['professor'] == 'Jaime Villate') #will returning the classes that he teaches
```

## Developing
Included there is a file 'hor_21.html' intended for training/testing the extraction of class information.
It is intended to be used with the scrapy shell with a terminal open on same folder as file.
```
scrapy shell ./ex_course.html
```

The file is loaded as response. Use response.xpath('«XPATH QUERRY»') to select things.