FROM python:3.9.7

WORKDIR /scrapper

COPY requirements.txt .

RUN pip install -r requirements.txt

# Just copy the code over, instead of using volumes like before
COPY scrapy.cfg .
COPY scrape_to_csv/ scrape_to_csv/
